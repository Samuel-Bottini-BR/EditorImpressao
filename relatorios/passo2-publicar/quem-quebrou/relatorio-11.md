# Passo 2 do plano da parte do Windows: décima primeira conferência de quem tentou quebrar (volta 12, 21/11/2026)

Do que se trata: é a ferramenta que prepara as versões do programa para o notebook do Kaique (o "publicar"), que roda
só no PC do Samuel. A volta 12 consertou os 3 problemas pequenos do relatório 10: a conferência automática que impede
as frases "em a pasta" (no lugar de "na pasta") ficou mais rigorosa; o roteiro da prova à vista ganhou uma pasta nova
e o registro do servidor fora do repositório; e duas frases antigas do formulário foram atualizadas.

Sou um agente novo nesta volta (D-815). Não escrevi nada desta volta nem das anteriores. Não mexi no código: as
mutações e as sondas foram numa cópia pequena (`git archive`, sem a pasta `relatorios/`) na pasta de rascunho desta
conversa, `v11q\`.

O que **não** fiz:

- não rodei o publicar, o PyInstaller, o vpk, o servidor das versões nem o `gh release` de verdade (D-785, item 8: a
  gerente roda, à vista); os comandos do roteiro foram conferidos lendo o código;
- não abri janela nem pergunta do Windows na tela do Samuel;
- não disparei rodada do GitHub (só li a 44948053084);
- um Python por vez, um arquivo de teste por vez, com a memória livre conferida antes (entre 2,3 e 3,2 GB, com o jogo
  aberto);
- não mexi em `C:\EditorImpressaoProva` (só listei), na pasta errada de 19/11 nem na junção `modelos`; nenhum comando
  de git que muda o `.git` (`--is-shallow-repository` = false antes e depois).

## Pedido

- Papel: quebrador
- Commit de partida: 8f89d941 (a ponta conferida: 47333171; o último código e teste: 7543fbde)
- Ramo: passo2-publicar-2026-11-19

## Veredito

**PRONTO PARA CONFERIR: os três consertos fazem o que a resposta do Samuel pediu, nenhum teste de antes da volta 11
mudou, e a conferência nova das frases acusa as cinco mutações do relatório 10 (provado: a antiga deixa passar as cinco,
a nova acusa as cinco).** Nada do que achei chega ao Kaique nem ao livro: o programa não mudou nesta volta e hoje
nenhuma frase do publicar está errada.

Ficam 2 baixos e 4 observações:

- **Baixo 1:** a conferência nova ainda deixa passar "em a pasta" de sete jeitos novos. O mais simples: pôr o nome
  sozinho entre chaves (`f"{destino.nome}"`) antes de somar ou de usar `.format`. Com isso, três das cinco mutações do
  relatório 10 voltam a passar nos 125 testes, com uma mudança de poucas letras. É a mesma família do relatório 10 (F2):
  a conferência olha o jeito comum e o vizinho passa.
- **Baixo 2:** três textos (o do teste, o da ajuda dele e o "Caminho e função" do formulário) dizem que "qualquer outro
  uso é acusado". O baixo 1 mostra que não é (F7).
- As observações: falsos alarmes possíveis no futuro (F8), o `Apagado` aceita o nome em qualquer posição, o roteiro não
  escreve inteiro o comando do servidor do item 19, e o Livro diz "segunda volta" do escritor na D-821.

Nunca "aprovado": só o Samuel aprova.

O que está certo (provado rodando, não só lido):

- **A reversão confere:** com a conferência de antes (`8f89d941`), as mutações G1 a G5 do relatório 10 passam; com a de
  agora (`47333171`), as cinco são acusadas (anexos `anexos-11/reversao-guarda-antiga-8f89d941.txt` e
  `reversao-guarda-nova-47333171.txt`; script `anexos-11/mutacoes-g-j.py.txt`, escrito por mim, não o do outro).
- **As contas do docstring conferem com a conferência nova:** 33 usos acusados em `edd39a9f`, 2 em `1624a05a`, 0 hoje
  (anexo `anexos-11/contar-juncoes-resultado.txt`).
- **Nenhuma frase certa de hoje é acusada:** 0 achados no código de hoje; li os 43 usos do nome do destino.
- **A pasta `versoes 6` não existe** (listei `C:\EditorImpressaoProva`: `versoes`, `versoes 2`, `versoes 3` e os
  registros `.log`).
- **No PC, um arquivo por vez, tudo passa;** no GitHub, a rodada 44948053084 testou `47110492` (que tem o último código,
  `7543fbde`; depois dele só o formulário mudou) e deu success em tudo.
- **O formulário passa no conferidor** (etapa "quebrar", com o pacote da volta 12): "O formulário passa", sem aviso.

## Decisões que esta tarefa precisa cumprir

Palavras copiadas do Livro da `obra-2026-10-26` (lido depois de `git fetch origin obra-2026-10-26`).

- **D-775** "o agente vai tentar quebrar antes de fazer o teste real na tela né?" · "ok". Esta é a etapa 3. **Cumprida.**
- **D-798** só quem confere escreve "PRONTO PARA CONFERIR", nunca sobre o que construiu. O formulário do outro não traz
  o rótulo; eu não construí nada. **Cumprida.**
- **D-807** o conjunto inteiro só no GitHub. Li a rodada, não rodei o inteiro no PC. **Cumprida.**
- **D-815** agente novo em cada volta de quem quebra. **Cumprida** (sou novo). Ver a observação 4 sobre a contagem
  das voltas do escritor.
- **D-816** "A , mas onde estamos antes de você fazer qualquer processo". Nada do que o publicar faz depois do pedido de
  liberar mudou (o programa não mudou; os `test_d816_*` passam no PC). **Cumprida.**
- **D-819** "sempre se deve se ver se é a coisa mais simples, ou melhor de se fazer". O plano da volta 12 traz o mais
  simples (a lista curta dos lugares aceitos) e o outro (um caso por jeito), com o porquê. **Cumprida.** Também uso
  essa regra no que peço no baixo 1.
- **D-820** "A". A pasta das ferramentas não mudou (`tests/test_pasta_das_ferramentas.py` 17 passam). **Cumprida.**
- **D-821** "ok, mas qual vai ser o proximo passo, todo resto está funcionando?". A frase da D-816 continua "na pasta"
  e a conferência das frases continua sem exceção. **Cumprida.**
- **D-822** "ok" (à pergunta "Conserto as 3 agora?"). (1) a conferência das frases acusa o uso do nome fora dos lugares
  da lista, e as mutações G1 a G5 são acusadas: **cumprida**, com o baixo 1 (ela deixa passar outros jeitos); (2) o
  roteiro com a `versoes 6` e o `--registro` fora do repositório: **cumprida** (observação 3); (3) as duas frases do
  formulário: **cumprida**. O programa não mudou (conferido no `git diff --stat`).
- **D-605 / CLAUDE.md §11.8** nenhum teste antigo muda para passar. Conferido linha a linha (abaixo). **Cumprida.**

## O que li

- `.claude/agents/verificador.md` e o `CLAUDE.md` inteiros (§4.6, §4.7, §11.8, §11.12 com os seis pontos, §11.13),
  `memoria/INDICE.md`, `memoria/licoes.md` e o caderno dos erros da `obra-2026-10-26` (famílias F1 a F10, com F2, F7 e
  F8 inteiras).
- Na cópia `passo2` (ponta `47333171`): o relatório 10 inteiro com o script das mutações dele; no ONDE-PAREI, o começo,
  o "Onde parei" das voltas 10 a 12, todas as partes "Volta 12" de cada seção e "A prova de verdade" inteira; o pacote
  da volta 12; o script e o resultado das mutações do escritor (`anexos/volta12-mutacoes-g*`); a prova 3 de 21/11.
- O Livro da `obra-2026-10-26`: D-775, D-798, D-807, D-815, D-816, D-819, D-820, D-821 e D-822, inteiras.
- O código: `git diff 8f89d941..47333171` inteiro; em `publicar_versao_kaique.py` os dois destinos, o `Apagado`, a
  `com_preposicao`, a conferência do motor publicado, o começo do `publicar` e as opções da linha de comando; em
  `servidor_das_versoes.py` as opções, a gravação do registro e o que ele faz com uma pasta que não existe.

## O que conferi

### A rodada do GitHub (lida, não disparada)

Rodada 44948053084 (21/11, 20:46 no relógio do GitHub): o log diz 71 vezes o commit `47110492`. Ele contém `7543fbde`
(conferido com `git merge-base --is-ancestor`), e de `47110492` até a ponta só o ONDE-PAREI mudou (`git diff --stat`).
Success no porteiro (o juiz da versão de teste), nos botões e prints da janela real e nas cinco partes do conjunto
inteiro. Lá: `test_publicar_versao.py` 125 passaram, `test_empacotar.py` 42 e 1 pulado, `test_pasta_das_ferramentas.py`
17.

### No PC, um arquivo por vez (na cópia `passo2`)

| Arquivo | Resultado |
|---|---|
| `tests/test_publicar_versao.py` | 125 passaram |
| `tests/test_empacotar.py` | 43 passaram |
| `tests/test_pasta_das_ferramentas.py` | 17 passaram |
| o conferidor do formulário, etapa "quebrar", com o pacote da volta 12 | "O formulário passa na etapa antes de ir ao agente que tenta quebrar" |

A cópia `passo2` ficou sem nenhuma mudança depois de cada rodada (`git status` mostra só a pasta nova deste relatório).

### Algum teste antigo mudou? (§11.8)

Li `git diff 8f89d941..47333171 -- tests/` linha a linha. Mudou só `tests/test_publicar_versao.py`, e só em dois
lugares, os dois da volta 11 (desta mesma tarefa, ainda não juntada) e os dois que a D-822 nomeia:

- a ajuda `_preposicao_a_mao` (reescrita) e as duas listas novas em cima dela (`_RECEBEM_O_NOME_DO_DESTINO`,
  `_ANTES_DO_NOME_NA_FRASE`); ninguém mais usa a ajuda (busca no repositório);
- o texto (docstring) de `test_volta11_nenhuma_frase_do_publicar_junta_em_ou_de_com_o_destino_a_mao`; o corpo do teste
  não mudou.

Nenhum teste de antes da volta 11 mudou. O programa não mudou (`git diff --stat`: só o teste e a pasta do relatório).

### Cada conserto resolve a causa, num lugar só? (§11.12)

- **Baixo 1 do relatório 10 (a conferência das frases):** o jeito escolhido é o certo (uma lista curta dos lugares
  aceitos, não um caso por jeito). Mas a regra do "começo da frase" é medida no começo de cada pedaço com chaves, não no
  começo da frase que vai para a tela: é por aí que o baixo 1 deste relatório passa.
- **Baixo 2 do relatório 10 (o roteiro):** o item 19 usa a `versoes 6` e diz para conferir antes que ela não existe;
  o item 2 dá o `--registro` num arquivo em `C:\EditorImpressaoProva\`. Conferi no `servidor_das_versoes.py`: a opção
  `--registro` existe, recebe um arquivo (as linhas são acrescentadas ao fim, `open("a")`) e a pasta dele é criada se
  faltar; sem a opção, o registro cai em `relatorios\servidor-das-versoes\`. O servidor abre com uma pasta que ainda não
  existe (a lista das versões fica vazia, não dá erro), então a ordem do item 19 (o servidor antes do motor) funciona.
  As opções `--pasta` e `--motor` do publicar existem, e a frase de parada sai com `--pasta "..."` entre aspas, como o
  roteiro espera.
- **Baixo 3 do relatório 10 (as duas frases do formulário):** as duas dizem agora que as palavras mudaram pela D-821 e
  o que o publicar faz, não. Acertado.

### A conferência das frases pega o vizinho? (F2, D-813)

Duas sondas, cada uma uma mutação por vez:

1. **Só a conferência** (`anexos-11/sonda-guarda.py.txt`): tira a ajuda do arquivo de teste pela árvore do Python e a
   roda sobre o publicar de hoje mudado em memória (nenhum arquivo do repositório é escrito). Resultado em
   `anexos-11/sonda-guarda-resultado.txt`.
2. **O arquivo de teste inteiro** (`anexos-11/mutacoes-g-j.py.txt`), numa cópia de `47333171`, com as mutações em
   frases que os testes de caminho não percorrem (como o relatório 10 fez). Resultado em
   `anexos-11/mutacoes-j-arquivo-inteiro-resultado.txt`. A cópia voltou igual ao git (conferido com `cmp`).

| Mutação | O que sai para quem lê | Conferência nova | 125 testes |
|---|---|---|---|
| J1 | `"o motor publicado em " + f"{destino.nome}" + ...` ("em a pasta") | passa | passam |
| J2 | `"não consegui liberar {} em {} ({})".format(etiqueta, f"{self.nome}", erro)` | passa | passam |
| J3 | `f"... (em {f'{destino.nome}'}) ..."` (chaves dentro de chaves) | passa | passam |
| J4 | `com_preposicao('por', destino.nome)` ("por a pasta") | passa | passam |
| J5 | `f"não consegui liberar {etiqueta} em a pasta {self.raiz} ..."` (o nome montado à mão) | passa | passam |
| J6 | `f"a assinatura lida de {getattr(destino, 'nome')} ..."` | passa | passam |
| J7 | `onde = f"{destino.nome}"` e depois `f"... liberada em {onde}"` | passa | passam |
| sem mutação | (o código de hoje) | passa | passam |

Nas sondas de memória também passam: o mesmo com `print(... , f"{destino.nome}")`, `" ".join([..., f"{...}"])`,
`"%s" % f"{...}"` e "em na pasta" (`f"... em {com_preposicao('em', ...)}"`). São acusados, como devem: o nome solto no
`print`, o `str(destino.nome)`, e os cinco G do relatório 10.

### A conferência acusa frase certa? (F8)

Hoje, nenhuma (0 achados). Mas acusaria, se alguém escrevesse (sonda de memória, `F8a` a `F8f`):
`com_preposicao("em", nome=destino.nome)` e `Apagado(etiqueta, onde=destino.nome, ...)` (o mesmo, com o nome do
argumento), `{destino.nome:<30}` no começo, "e a pasta", "com a pasta", e um uso que não é frase
(`if destino.nome: ...`). O escritor escreveu a ressalva só do "e ".

## Achados

1. **BAIXO: a conferência nova das frases deixa passar "em a pasta" de sete jeitos novos.**
   - Onde: `tests/test_publicar_versao.py`, `_preposicao_a_mao`, a função `aceito`: o nome dentro de chaves é aceito
     quando está no começo do pedaço com chaves (`i == 0`, ou só espaço antes), mesmo que esse pedaço seja depois somado
     a um "em ", passado a `.format`, guardado numa variável ou posto dentro de outras chaves.
   - Provado: J1, J2, J3, J6 e J7 acima (os três G mais comuns do relatório 10 voltam a passar com `f"{...}"` em volta
     do nome). Também passam J5 (a frase escrita com "em a pasta {self.raiz}" dentro do próprio destino, que não usa o
     `.nome`) e J4 (a `com_preposicao` com "por", já escrito pelo escritor como ressalva e posto na Lista de espera).
   - Hoje nenhuma frase está errada (0 achados; li os 43 usos do nome do destino). Nada disso chega ao Kaique: é a rede
     de proteção de um teste. É a família F2 de novo.
   - O que pedir (D-819: o mais simples e o outro):
     - **O mais simples:** o pedaço com chaves só conta como "começo da frase" se ele for a frase inteira que sai (o que
       vai direto para `Parou`, `PublicacaoLiberada`, `print`, `append` ou `return`), e um pedaço que é só o nome
       (`f"{destino.nome}"`) conta como uso solto. Isso pega J1, J2, J3 e J7. Junto, uma segunda conferência curta, pelo
       texto: nenhum texto do publicar tem " em a pasta", " de a pasta", " em o GitHub" ou " de o GitHub" (pega o J5).
     - **O outro:** deixar como está e a ressalva do formulário ganhar estes sete jeitos. Uma conferência que lê o
       código nunca vai ser completa (o `getattr`, J6, sempre escapa); o teste de caminho (`test_volta11_as_frases_...`)
       já confere o que sai de verdade nos caminhos principais.
     - A gerente escolhe; minha opinião é que o primeiro vale a pena se for feito numa volta só, e que depois disso a
       próxima volta não deve procurar mais vizinhos desta mesma conferência (são cada vez menos prováveis).

2. **BAIXO: três textos prometem mais do que a conferência faz.**
   - Onde: o texto de `test_volta11_nenhuma_frase_...` ("a guarda acusa qualquer uso do nome do destino fora dos lugares
     aceitos"), o da ajuda `_preposicao_a_mao` ("qualquer outro uso é acusado") e o ONDE-PAREI, "Caminho e função",
     Volta 12 ("conferida ... sobre todos os usos ... (f-string, soma, variável, `.format`, qualquer chamada)").
   - Provado: o achado 1. É a família F7 (o escrito não bate com o código); o conferidor do formulário não pega isso.
   - O que pedir: se o achado 1 for consertado, os textos ficam verdadeiros; se não, trocar "qualquer" pelo que ela pega
     de fato e citar os jeitos que passam.

3. **OBSERVAÇÃO 1: falsos alarmes possíveis no futuro (F8).**
   - A conferência acusaria código certo: o nome passado com o nome do argumento (`nome=`, `onde=`), com alinhamento
     (`:<30`), depois de "e " ou "com ", e qualquer uso que não é frase (uma comparação). Para os três primeiros basta
     acrescentar um lugar à lista; para o último, a lista não tem onde: seria preciso mudar a conferência.
   - Hoje nenhum desses existe. Só anoto para que a ressalva do formulário (que cita só o "e ") fique completa.

4. **OBSERVAÇÃO 2: o `Apagado` aceita o nome em qualquer posição.**
   - `Apagado(destino.nome, etiqueta, existia=False)` (as duas trocadas) passa na conferência e daria "a pasta ...: não
     existia em v1.2.0". Não é o defeito da preposição, e hoje as duas chamadas estão certas. Basta saber.

5. **OBSERVAÇÃO 3: o comando do servidor do item 19 não está escrito inteiro.**
   - O item 19 diz "com o servidor do item 2 servindo essa pasta (`--registro "...servidor-prova4.txt"`)", e o item 2
     tem `--pasta <pasta de prova>` sem aspas. Com a `versoes 6` (com espaço), quem trocar só o nome sem pôr aspas recebe
     do servidor "unrecognized arguments: 6" e ele não abre (lido no código: só há opções, nenhum argumento solto). Não
     estraga nada, mas é o tipo do baixo 1 do relatório 9 (roteiro que não dá para seguir ao pé da letra).
   - Sugestão: escrever o comando inteiro no item 19:
     `D:\programas\EditorImpressao\.venv\Scripts\python.exe servidor_das_versoes.py --pasta "C:\EditorImpressaoProva\versoes 6" --registro "C:\EditorImpressaoProva\servidor-prova4.txt"`.
   - Detalhe: na mesma pasta já existe `prova4.log`, de 20/11 (outra numeração). O arquivo novo tem outro nome e não
     colide; só pode confundir quem ler depois.

6. **OBSERVAÇÃO 4: o Livro conta as voltas do escritor de dois jeitos.**
   - A D-821 diz "escritor da volta 11 do passo 2 (segunda volta dele, D-815)"; o ONDE-PAREI diz que a volta 11 foi a
     primeira dele (escritor novo) e a volta 12 a segunda e última. Se a D-821 estiver certa, a volta 12 seria a
     terceira, o que a D-815 não deixa. Pelo ONDE-PAREI (a volta 11 com uma pausa para a pergunta da D-821, retomada pelo
     mesmo agente), a conta certa é a do ONDE-PAREI, e a frase da D-821 no Livro é que está errada. É da gerente acertar.

## O que falta

- Para a prova à vista: nada que impeça; a observação 3 é só para seguir o item 19 sem tropeço.
- Para juntar: os baixos 1 e 2 (ou a decisão da gerente de deixá-los como ressalva).

## Para a gerente: o que ficou fora do projeto

Na pasta de rascunho desta conversa,
`C:\Users\fotog\AppData\Local\Temp\claude\b9ca076ad002e817\52740cda-b98f-4183-a448-ea9ff84b0439\scratchpad\v11q\`
(criada nesta tarefa, uns 60 MB):

- `novo\` e `antigo\`: o código de `47333171` e de `8f89d941` por `git archive`, sem a pasta `relatorios/` (30 MB
  cada). A `novo\` voltou igual ao git depois das mutações (conferido com `cmp`, sem contar o fim de linha).
- Os scripts e resultados (cópias em `quem-quebrou/anexos-11/`), o publicar de `edd39a9f` e de `1624a05a` (para a
  conta) e o registro da rodada 44948053084 (uns 0,9 MB).

Continuam lá, de antes desta tarefa e não tocados por mim: `v10q\` (2,5 GB, do relatório 10), `v11\` e `v12\` (do
escritor) e os outros arquivos soltos. O pytest também cria pastas em
`C:\Users\fotog\AppData\Local\Temp\pytest-of-fotog\` (ele guarda só as últimas). Não apaguei nada em lugar nenhum.

## Fontes

- Python 3.14, módulo `ast`: um texto com chaves (f-string) vira `JoinedStr`, com partes `Constant` e
  `FormattedValue`; dois pedaços lado a lado sem `+` viram um só (por isso a frase de duas linhas é vista inteira); com
  `+` são dois `JoinedStr` separados (por isso J1 e J7 passam: o segundo pedaço começa no nome); `getattr` é uma chamada,
  sem `Attribute` (por isso J6 passa).
- Python, módulo `argparse`: palavra solta que nenhuma opção espera dá o erro "unrecognized arguments" e o programa sai
  sem abrir (observação 3).
- `servidor_das_versoes.py`, `principal` (as opções e o registro) e `Versoes.publicacoes` → `DestinoPasta.liberadas`
  (pasta que não existe: lista vazia).
- Rodada do GitHub 44948053084 (lida com `gh run view`).
