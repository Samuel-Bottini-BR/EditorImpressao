# Passo 2 do plano da parte do Windows: oitava conferência de quem tentou quebrar (voltas 8 e 9, 21/11/2026)

Sou um agente novo nesta volta (D-815). Não escrevi este código e não conferi as voltas anteriores. Não mexi no código
do outro: as minhas mudanças foram em cópias (`git archive`), na pasta de rascunho `quebra9\`.

O que **não** fiz:

- não rodei o publicar, o PyInstaller, o vpk nem o `gh release` de verdade (D-785, item 8: a gerente roda, à vista);
- não abri janela, console nem pergunta do Windows na tela do Samuel (o git e o PowerShell da peça abrem sem janela);
- não disparei rodada do GitHub (só consultei a 44847777899 e a 44859326833);
- não rodei `tests/test_ocr_kraken.py` (abre o motor de 1 GB) nem nada pesado ao mesmo tempo: um Python por vez;
- não mexi em `C:\EditorImpressaoProva` (só li o `prova6b.log`), na pasta errada de 19/11 (só listei; a data continua
  19/11/2026 15:44) nem na junção `modelos`.

## Pedido

- Papel: quebrador
- Commit de partida: 82b610f9
- Ramo: passo2-publicar-2026-11-19

## Arquivos que vou mexer

- `core/pasta_das_ferramentas.py`
- `tests/test_pasta_das_ferramentas.py`
- `regras_dos_agentes/conversa_com_o_git.py`
- `regras_dos_agentes/repositorio_de_prova.py`
- `compilar_st_ferramentas.py`
- `publicar_versao_kaique.py`
- `empacotar.py`
- `montar_motor_kraken.py`
- `compilar_detector_gravura.py`
- `core/ocr_kraken.py`
- `atualizacao.py`
- `tests/test_empacotar.py`
- `tests/test_publicar_*.py`
- `tests/test_ocr_kraken.py`
- `relatorios/passo2-publicar/`

(Só mexi de verdade em `relatorios/passo2-publicar/`: este relatório e `quem-quebrou/anexos-8/`. Os outros arquivos da
lista só foram lidos, ou mudados em cópias à parte.)

## Veredito

**NÃO ESTÁ PRONTO: o conserto do defeito 1 acha o lugar certo quando o git responde, mas, numa cópia de trabalho, se o
git não responder, ele volta em silêncio ao lugar errado de antes, e lá ainda existe a pasta errada de 19/11 com o
Visual C++ dentro. Provei com o git de verdade.** É o mesmo defeito que a volta 9 consertou, por outro caminho, e
nenhuma frase avisa. O outro escreveu esse caso como "não acontece"; acontece, por exemplo, quando o HD externo vai para
outro Windows (o git recusa o repositório por ser de outro dono).

Ficam também 2 baixos e 7 observações (abaixo). Nada disso muda o que o Kaique recebe hoje. Nunca "aprovado": só o
Samuel aprova.

O que está certo (provado rodando, não só lido):

- **Da cópia de trabalho de verdade (`passo2`), os seis lugares acham a pasta certa** e o motor certo
  (`D:\programas\EditorImpressao-arquivos\ferramentas\motor-kraken`). A pergunta ao git levou 0,125 s.
- **O programa do Kaique (simulado empacotado) nunca pergunta ao git e não quebra sem a peça do git:** nenhum processo
  aberto, o motor procurado só ao lado do programa (sonda S3). Dentro da janela do programa o git também não é chamado:
  o Kraken está desligado no programa (`SEGUNDA_OPINIAO_DO_KRAKEN = False`), então só a linha de comando do diagnóstico
  e os testes chegam lá.
- **O caminho escrito de outro jeito (D-813) dá o mesmo lugar:** minúsculas, barras, `\\?\`, nome curto,
  `\\localhost\D$` e `..` (sonda S5).
- **Os três scripts que gravam param com a frase e não criam nada** quando a pasta das ferramentas não existe (rodei os
  três de verdade numa cópia sem repositório).
- **A frase do apagar** sai de um lugar só, nos dois destinos e para a versão e o motor; o caminho de erro antes do
  pedido de liberar usa a mesma; depois do pedido de liberar nada se apaga (D-816, lido: as linhas não mudaram).
- **A leitura única da versão do Visual C++:** o programa instalado faz o mesmo de antes em todos os casos, menos o
  arquivo que não é UTF-8 (antes dava erro; agora lê). Esse arquivo o publicar recusa, e a assinatura do pacote impede
  que chegue ao Kaique (sonda S7).
- **A reversão confere com a do outro:** volta 8, 10 dos testes novos falham no código antigo e 111 passam; volta 9, os
  2 testes do defeito e o do pacote falham.
- **Nenhum teste antigo mudou** (de `21f1fc50` a `011b06d0` os testes só ganharam linhas). As duas rodadas do GitHub
  passaram, sobre o código certo.

## Decisões que esta tarefa precisa cumprir

Palavras copiadas do Livro (`obra-juncao`, `docs/plano/DECISOES.md`), e como as achei nesta entrega.

- **D-605** "A partir de agora, nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já está escolhido e testado, coisas novas não podem criar novos problemas, essa é uma nova regra que todos os agentes precisam ler"
  Aqui: **cumprida**. Nenhum teste antigo mudou; da pasta principal os seis lugares dão o mesmo de antes; o programa
  instalado faz o mesmo com o arquivo da versão (só o não-UTF-8 muda, e não chega ao Kaique). O que já funcionava em
  volta (o porteiro, que usa a mesma peça do git) passou na rodada 44859326833.
- **D-727** "pode, se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador né"
  Aqui: **cumprida** (não muda): o Visual C++ continua indo no pacote; a montagem só não cria mais a pasta das
  ferramentas no lugar errado.
- **D-767** "não faça mais nada escodindo ou de mentira" · "não quero fazer consertos quero que funcione" · "quero que faça as coisas certas e sem bugs ou erros, deveria ter pensado nesses erros na hora de montar a estrutura do atualizador e testes a distancias"
  Aqui: **pela metade**. Os testes do defeito 1 usam o git de verdade, numa cópia de trabalho de verdade (bom). Mas o
  "git que demora" foi provado com um limite de 1 microssegundo e um git que responde na hora; com um git que demora de
  verdade, o limite não segura no PC do Samuel (achado 2). E o caso "sem resposta do git numa cópia" foi pensado e
  deixado de lado como "não acontece" (achado 1).
- **D-773** "A"
  Aqui: não se aplica a estas voltas (nenhuma versão de prova foi servida nem publicada).
- **D-775** "o agente vai tentar quebrar antes de fazer o teste real na tela né?" · "ok"
  Aqui: **cumprida** por este relatório; achei um médio, então, pela D-775, volta ao passo 1 antes da prova à vista.
- **D-776** "Sim, no C só tem que cuidar para não encher o disco C inteiro"
  Aqui: não muda (o publicar continua montando no C:, com a reserva; não toquei).
- **D-777** "mas dai vai fazer quais versões?" · "ok, fica assim"
  Aqui: não muda.
- **D-785** "ok, mais ainda existem mais casos na opção A" · "ok"
  Aqui: **cumprida** por mim (nada à vista rodei; o publicar fica para a gerente).
- **D-788** "1" (a primeira opção)
  Aqui: **cumprida**. Empacotado, o motor é procurado primeiro ao lado do programa, como hoje, e nada é perguntado ao
  git (sonda S3). A peça do git fica fora do pacote pela lista de exclusão (lido no PyInstaller 6.21: o nome excluído
  vira um módulo vazio; que os submódulos também saiam é dedução; o pacote de verdade só a prova mostra).
- **D-789** "mas iria demorar mais toda vez que eu fosse fazer a compilação né?" · "A"
  Aqui: não muda.
- **D-795** "porque fazer isso?" · "porque ter um instalador pequeno então?" · "não tem nenhuma documentação dizendo para o que isso serve?" · "ok"
  Aqui: não muda (o apagar do Setup.exe não foi tocado).
- **D-815** "pode conferir se não está ocorrendo alucinação por estar com contexto cheio" · "estou falando do agente que está trabalhando" · "esses agentes que você criou, sempre que vai fazer uma tarefa nova, chama outro com a mesmas instruções ou ifac rodando sempre o mesmo com memorias compactadas?" · "ok"
  Aqui: **cumprida**: sou agente novo nesta volta. O escritor das voltas 8 e 9 é o mesmo (a segunda e última volta
  dele): a próxima volta de conserto vai para um escritor novo.
- **D-816** "A , mas onde estamos antes de você fazer qualquer processo"
  Aqui: **cumprida**: depois do pedido de liberar, nada se apaga (as linhas de `publicar_arquivos` que decidem isso não
  mudaram; o teste da D-816 passou na rodada).
- **D-817** "pode"
  Aqui: **cumprida** (não muda): o teste trocado pela D-817 continua o mesmo.
- **D-818** "vai ter que reprogramar?" · "A"
  Aqui: **cumprida**: a pasta já montada continua conferida pela mesma régua; a leitura do arquivo da versão passou a
  ser a mesma do programa instalado (volta 8).

## O que li

- As regras do verificador (`.claude/agents/verificador.md`), o `CLAUDE.md` inteiro da cópia `passo2`, a memória
  (`memoria/INDICE.md`; `memoria/geral/atualizador.md` da pasta principal, porque a cópia `passo2` não a tem), o catálogo
  dos erros da `obra-juncao` (as famílias F1 a F10) e o pacote `anexos/pacote-quem-quebra-volta9.md`.
- No Livro da `obra-juncao`, as linhas inteiras de D-605, D-727, D-767, D-773, D-775, D-776, D-777, D-785, D-788,
  D-789, D-795, D-813, D-815, D-816, D-817 e D-818 (o pacote diz "não achada" para D-815 a D-818; elas existem no Livro
  da `obra-juncao`, nas linhas 1105 a 1108).
- O ONDE-PAREI do escritor: "Onde parei", as partes Volta 8 e Volta 9 de "A causa", "O que pode falhar", "O que li",
  "Ressalvas", "Cada proteção" e "A prova de verdade"; os anexos de reversão e de mutação das duas voltas.
- O código: o diff de `21f1fc50` a `011b06d0` inteiro (13 arquivos), `core/pasta_das_ferramentas.py` inteiro, a peça
  do git, os seis lugares, o caminho de erro de `publicar_arquivos`, o `instalar_visual_c_se_faltar` e quem o chama.
- **Peças de fora, lidas na fonte:** o `subprocess.run` do Python 3.14 (`Lib/subprocess.py`, linhas 554 a 570: no
  Windows, depois de matar o programa que passou do tempo, ele chama `communicate()` sem limite); o `ModuleGraph` do
  PyInstaller 6.21 (`lib/modulegraph/modulegraph.py`, linhas 926 a 929: cada nome excluído vira `None` nos nós
  preguiçosos). Do git: a mensagem de recusa por dono diferente, vista rodando (`fatal: detected dubious ownership`).
- O registro da prova 6b (`C:\EditorImpressaoProva\prova6b.log`, UTF-16, só lido): "não existe
  D:\programas\EditorImpressao\.claude\worktrees\EditorImpressao-arquivos\ferrame...".

## O que conferi nas falhas, nas peças de fora e nos caminhos

### As rodadas do GitHub (consultadas, não disparadas)

- **44847777899 (volta 8): success na tentativa 2**, sobre o ramo em `5462d882` (o commit aparece 60 vezes no registro).
- **44859326833 (volta 9): success na tentativa 1**, sobre o ramo em `0e36d0a4` (= `011b06d0` mais o formulário):
  `test_pasta_das_ferramentas.py` 10 passaram; `test_empacotar.py` 42 passaram e 1 pulou (o do Tesseract não
  instalado, antigo); `test_publicar_versao.py` 121 passaram; `test_ocr_kraken.py` 27 passaram e 6 pularam (lá não há
  motor).

### A prova de reversão (anexo `anexos-8/reversao-no-codigo-antigo.txt`)

Rodei de novo, em cópias minhas:

- **Volta 8:** os testes de `011b06d0` no código de `21f1fc50`: **10 falham, 111 passam** (os 10 do apagar e da
  leitura única), igual ao anexo do outro. Os que passam lá cobram proteções que já existiam (o outro provou com U8 a
  U12).
- **Volta 9:** os testes de `011b06d0` (com a peça do git e o repositório de prova novos por cima, só para o teste
  rodar) no código de `5c22a12d`: **2 falham** (os seis lugares da cópia; a montagem que criava a pasta), **1 passa** (o
  "da pasta principal, nada muda", que é de não estragar, não de reversão), **7 pulam** (pedem a função nova), e o teste
  do pacote **falha**. Igual ao do outro. Os 7 que pulam não provam reversão, mas as mutações dele os cobrem.

### Os casos que podem falhar, rodados com o git de verdade (anexos `sondas-s1-s2-s4.txt`, `sonda-s5.txt`, `sonda-s6-limite.txt`)

| Caso | O que acontece | Certo? |
|---|---|---|
| Da cópia `passo2`, git normal | a pasta certa, o motor certo, 0,125 s | sim |
| Da cópia, **sem git no caminho** | a pasta errada de 19/11, que existe; o Visual C++ é tirado de lá; "pode gravar" diz sim | **não** (achado 1) |
| Da cópia, **o git recusa o dono** | o mesmo do de cima | **não** (achado 1) |
| `GIT_DIR` herdado (gancho do commit) | a pasta certa (teste do outro; a mutação P8 dele é acusada) | sim |
| O caminho escrito de 7 jeitos (D-813) | o mesmo lugar nos 7 | sim |
| Pasta com espaço no nome | certo (os testes do outro rodam numa) | sim |
| Pasta principal sem a pasta das ferramentas | a frase e nada criado (teste do outro, e os três scripts rodados por mim) | sim |
| **Git que demora de verdade** | limite de 2 s: devolveu só aos 14,9 s, quando eu fechei a entrada do git | **não** (achado 2) |
| Cópia sem repositório dentro de outro repositório | o git sobe as pastas e acha o outro; no PC do Samuel dá a pasta certa por acaso | observação 9 |
| Empacotado | nada perguntado ao git, nenhum processo aberto | sim |

### As mutações minhas (anexo `anexos-8/mutacoes-b-resultado.txt`; script `mutacoes_b.py.txt`)

Diferentes das P1 a P11 e U1 a U12. Uma por vez, numa cópia de `011b06d0`, devolvida ao original byte a byte.

| | O que desliguei | Acusada? |
|---|---|---|
| B1 | o `montar_motor_kraken` deixa de parar quando a pasta das ferramentas não existe | **não** |
| B2 | o `compilar_detector_gravura` deixa de parar | **não** |
| B3 | o `compilar_st_ferramentas` deixa de parar | **não** |
| B4 | o `montar_motor_kraken` só confere quando destino **e** downloads são os de fábrica | **não** |
| B5 | "pode gravar?" olha a pasta `EditorImpressao-arquivos`, e não a `ferramentas` dentro dela | **não** |
| B6 | a peça do git aceita qualquer pasta comum (deixa de exigir `.git`) | **não** |
| B7 | a pergunta deixa de tirar só a `GIT_COMMON_DIR` do ambiente | **não** |
| B8 | o git que passa do tempo deixa de virar a frase da peça | sim |
| B9 | o caminho de erro apaga sem o "acabou de criar" | sim |

### O que já funcionava em volta (§11.8)

- Nenhum teste antigo mudou: o diff dos testes de `21f1fc50` a `011b06d0` só tem linhas novas.
- A peça do git agora abre todo git sem janela (também os do porteiro). A rodada 44859326833 passou com o porteiro e as
  conferências.
- `tests/test_ocr_kraken.py` cobra "pelo menos dois lugares": empacotado ficam dois (antes três); continua passando.

## Caminhos que o outro não listou

1. **Sem resposta do git, numa cópia de trabalho** (sem git no caminho, o git que recusa o dono, o git que passa do
   limite): o outro listou "sem git" só para a pasta principal e para a cópia sem repositório. Numa cópia de trabalho, a
   conta de antes é justamente a conta errada, e ela é usada calada (achado 1).
2. **O git do caminho do Windows é um lançador** (`C:\Program Files\Git\cmd\git.exe` abre o `mingw64\bin\git.exe`): é
   esse o git que o Python acha quando roda fora do Git Bash (PowerShell, atalho, Explorer). O limite de tempo só mata o
   lançador (achado 2).
3. **A pasta `EditorImpressao-arquivos` existe, mas sem `ferramentas` dentro:** nenhum teste a usa (a mutação B5 passa).
4. **O main dos três scripts que gravam** (`montar_motor_kraken`, os dois compiladores): nenhum teste o chama (B1 a B4
   passam).

## Falhas não pensadas e resultado não conferido

- **Resultado não conferido (F5):** quando o git não responde numa cópia, a regra dá a pasta errada como certa e
  ninguém fica sabendo. A frase de "não dá para gravar" chama de "pasta principal" uma pasta que é só a de cima do
  código (o git não disse nada).
- **Proteção que não protege (F3):** o limite de tempo do git, no PC do Samuel, não limita (achado 2). O teste dele usa
  1 microssegundo e um git que responde em 0,1 s: passa porque o git é rápido, não porque o limite funciona.
- **Proteções sem teste (F3, pela terceira volta seguida neste passo):** as quatro dos scripts que gravam (B1 a B4) e a
  B5. O "Cada proteção" do outro não as lista.

## As regras que conferi

- **§11.12.1, uma peça só:** a pasta das ferramentas tem agora um lugar só (grep de `RAIZ.parent`, `parents[`,
  `.parents`, `.parent.parent` e `EditorImpressao-arquivos` fora de `tests/`: os seis lugares chamam
  `core/pasta_das_ferramentas.py`; sobra só o `rodada_gravura_1_2.py`, que acha o **acervo**, já anotado pelo outro).
  Mas a peça do git faz o próprio limite de tempo, quando a peça do Windows já tem o jeito de fechar um programa com os
  filhos dele (o "grupo do Windows" do vpk e do gh, `core/windows.py`): achado 2.
- **§11.12.2, nada dá como feito o que não conferiu:** achado 1.
- **§11.12.3, a lista das falhas:** feita pelo outro, com um caso marcado como "não acontece" que acontece (achado 1).
- **§11.12.4 e D-767, peça de mentira:** os testes do defeito 1 usam o git de verdade (bom); o do "git que demora" não
  prova o que diz (achado 2); o do "empacotado" troca `sys.frozen` (ele diz que é só lógica, e é).
- **§11.12.6 e D-813, ler a peça de fora e tudo o que ela aceita:** os jeitos de escrever o caminho estão cobertos
  (sonda S5). Faltou ler o `subprocess.run` no Windows (achado 2) e o lançador do Git for Windows.
- **§11.8 e D-605:** nenhum teste antigo mudou.
- **§4.7, teste de reversão:** confere (refiz as duas).
- **§10.5, docstring:** todo arquivo e função tocados têm. Um docstring de teste promete mais do que o teste cobra
  (observação 4).

## Achados

1. **MÉDIO: numa cópia de trabalho, quando o git não responde, a regra volta calada à pasta errada de 19/11, e usa o
   Visual C++ de lá.**
   - Onde: `core/pasta_das_ferramentas.py:62-66` (`pasta_principal`: `GitFalhou` → `return codigo`, a pasta do próprio
     código) e `core/pasta_das_ferramentas.py:72` (a conta, guardada por processo).
   - Provado rodando (anexo `sondas-s1-s2-s4.txt`), de dentro da cópia de verdade `passo2`: sem o git no caminho do
     Windows, e com o git recusando o repositório por dono diferente (`GIT_TEST_ASSUME_DIFFERENT_OWNER=1`, que faz o
     git de verdade dar a mesma recusa de quando o HD externo vai para outro Windows ou o Windows é reinstalado:
     "fatal: detected dubious ownership"), a pasta das ferramentas vira
     `D:\programas\EditorImpressao\.claude\worktrees\EditorImpressao-arquivos\ferramentas`. Ela existe; "pode gravar"
     responde que sim; `empacotar.DOWNLOADS` aponta para lá e acha o `vc_redist.x64.exe` de 25.635.768 bytes da pasta
     errada; o motor não é achado. É o defeito 1 inteiro, sem nenhuma frase.
   - Lido na fonte: o publicar continua mesmo com o git falhando (o commit vira "não deu para ler", `empacotar.py:1704-1711`
     e `publicar_versao_kaique.py:943-948`), então nada para antes.
   - O outro escreveu esse caso nas "Ressalvas" ("sem git num computador com uma cópia de trabalho (não acontece: a
     cópia é feita pelo git)"). A cópia é feita pelo git, mas o git pode deixar de responder depois.
   - Por que médio: é o defeito que esta volta consertou, voltando por outro caminho, em silêncio. Não chega ao Kaique
     (o Visual C++ de lá é o oficial, e a régua da assinatura confere), mas o `montar_motor_kraken` e os compiladores
     gravariam na pasta errada sem avisar.
   - O que pedir: quando a pasta do código tem um `.git` que é **arquivo** (é uma cópia de trabalho, e isso se vê sem
     perguntar ao git) e o git não responde, **não usar a conta de antes**: a regra diz "não sei", e quem procura ou
     grava para com a frase do porquê (ex.: "não consegui perguntar ao git onde está a pasta principal desta cópia: o
     git disse ..."). Com o teste no repositório de prova, da cópia de trabalho, com o git de verdade recusando o dono e
     com o git fora do caminho. E corrigir a ressalva.

2. **BAIXO: o limite de tempo da pergunta ao git não segura no PC do Samuel.**
   - Onde: `regras_dos_agentes/conversa_com_o_git.py:52-56` (`_rodar`, `timeout=limite_s`).
   - Lido na fonte: o `subprocess.run` do Python 3.14, no Windows, depois de matar o programa que passou do tempo, espera
     sem limite a saída dele (`Lib/subprocess.py:557-565`). O git que o Windows acha fora do Git Bash é o lançador
     `C:\Program Files\Git\cmd\git.exe`, que abre o git de verdade como filho: matar o lançador não mata o filho, e a
     saída só fecha quando o filho termina.
   - Provado rodando (anexo `sonda-s6-limite.txt`): um git de verdade esperando de verdade (lendo a entrada, que eu
     deixei aberta), com limite de 2 s. Pelo lançador, a peça devolveu aos **14,9 s**, e só porque eu fechei a entrada
     aos 15 s; sem isso, não teria fim. Pelo git direto, devolveu aos 2,0 s.
   - O teste dele (`tests/test_pasta_das_ferramentas.py:222-225`) usa um limite de 1 microssegundo com um git que
     responde em 0,1 s: passa porque o git é rápido.
   - Por que baixo: o `rev-parse` quase nunca trava. Mas o limite está escrito como proteção e não protege.
   - O que pedir: abrir o git da peça do jeito que a peça do Windows já abre o vpk e o gh (o grupo do Windows, que
     fecha o programa com os filhos), em vez de uma conta própria de tempo; e um teste com o git do caminho do Windows
     esperando de verdade (como a sonda S6) que cobre a volta perto do limite.

3. **BAIXO: cinco proteções novas sem teste que as acuse (a família F3 de novo, terceira volta seguida neste passo).**
   - Onde: `montar_motor_kraken.py:636-640` (B1, B4), `compilar_detector_gravura.py:283-287` (B2),
     `compilar_st_ferramentas.py:211-215` (B3), `core/pasta_das_ferramentas.py:90` (B5).
   - Provado (mutações B1 a B5): passam em todos os testes. Rodei os três scripts de verdade, sem as mutações, numa
     cópia sem a pasta das ferramentas: os três param com a frase e não criam nada. Então hoje está certo; é a proteção
     que pode sumir calada. São justamente os lugares que criaram a pasta errada de 19/11.
   - O que pedir: um teste que rode o `main` de cada um dos três, com o padrão, de dentro da cópia de prova sem a pasta
     das ferramentas, e cobre a frase e nenhuma pasta nova; o caso de só o `--destino` passado (B4); e o caso de
     `EditorImpressao-arquivos` existir sem `ferramentas` dentro (B5).

4. **OBSERVAÇÃO: o docstring do teste do pacote promete mais do que ele cobra.**
   - Onde: `tests/test_empacotar.py:610-614` diz "E a propria regra esta no pacote (o core/ocr_kraken a usa)", e o
     teste só confere a linha de comando do PyInstaller.
   - O pacote de verdade só a prova mostra (ver "O que falta para a prova à vista", item 1).

5. **OBSERVAÇÃO: duas mutações pequenas na peça do git sem teste** (B6: aceitar qualquer pasta comum, não só `.git`;
   B7: deixar de tirar só a `GIT_COMMON_DIR`). Hoje o código está certo; os testes só usam `.git` e só põem `GIT_DIR` e
   `GIT_INDEX_FILE`. A lista das variáveis foi escrita à mão; o git tem a lista oficial (`git rev-parse
   --local-env-vars`). Não peço conserto; anoto.
   - Onde: `regras_dos_agentes/conversa_com_o_git.py:88` (B6) e `regras_dos_agentes/conversa_com_o_git.py:35` (B7).

6. **OBSERVAÇÃO: a frase do apagar sai "foi apagada de a pasta ..." e "de o GitHub (...)".**
   - Onde: `publicar_versao_kaique.py:641-643` com `DestinoPasta.nome` (`:312`) e `DestinoGitHub.nome` (`:452`).
   - É português sem a contração ("da pasta", "do GitHub"); o roteiro (item 18) já espera assim. O sentido está certo.

7. **OBSERVAÇÃO: o programa instalado lê diferente só o arquivo da versão que não é UTF-8.**
   - Provado (anexo `sonda-s7-visual-c.txt`, antes e depois, 18 casos): sem arquivo, certo, vazio e com a marca de
     UTF-8, igual. UTF-16 e bytes estranhos: antes, erro; agora, lê, e com um Visual C++ velho instalado não reinstala e
     dá a preparação como feita.
   - Não chega ao Kaique: o publicar recusa esse arquivo, e a assinatura do pacote impede trocá-lo depois (D-789). O
     outro já tinha escrito isso.
   - Onde: `atualizacao.py:1219-1234` (a leitura única) e `atualizacao.py:1250-1252` (quem a usa no programa instalado).

8. **OBSERVAÇÃO: "está empacotado?" e "30 segundos" escritos em dois lugares.** `core/pasta_das_ferramentas.py:49-51`
   (`empacotado()`) e `core/ocr_kraken.py:166` (`getattr(sys, "frozen", False)`, que já existia); `LIMITE_DO_GIT_S = 30`
   (`core/pasta_das_ferramentas.py:43`) e o padrão `limite_s=30` da peça do git (`conversa_com_o_git.py:76`). Hoje dão o
   mesmo.

9. **OBSERVAÇÃO: a cópia sem repositório dentro de outro repositório.** O outro anotou. Conferi a conta (dedução, não
   rodei): no PC do Samuel, um `git archive` desfeito dentro da pasta principal acha a pasta principal dela, que é a
   certa. No Windows do GitHub, a cópia dentro do repositório baixado acharia a pasta ao lado dele, que não existe: a
   frase e nada criado. O teste impede o git de subir, então esse caso do GitHub não é cobrado.
   - Onde: `core/pasta_das_ferramentas.py:62-66` e `tests/test_pasta_das_ferramentas.py:198` (o `GIT_CEILING_DIRECTORIES`).

10. **OBSERVAÇÃO: a peça do git sem janela vale também para o porteiro.** Com isso, um git que precisasse perguntar
    usuário e senha no terminal não pergunta mais (falha, em vez de esperar). Dedução; o porteiro não pede senha hoje.
    - Onde: `regras_dos_agentes/conversa_com_o_git.py:32` e `regras_dos_agentes/conversa_com_o_git.py:54`.

## O que falta para a prova à vista

A prova só depois de consertado o achado 1 (D-775). Para a gerente repetir com o Samuel só o que mudou, os itens 18 e 19
bastam para o publicar, com três acréscimos:

1. **O pacote do Kaique sem a peça do git (D-605, D-788).** Depois da montagem do item 15, listar o que o PyInstaller pôs
   no programa (`pyi-archive_viewer` no `dist\EditorImpressao\EditorImpressao.exe`): não pode ter `regras_dos_agentes`, e
   tem de ter `core.pasta_das_ferramentas`. E abrir uma vez o programa montado (até a janela), para ver que nada
   importava a peça tirada. Hoje isso é só conta e leitura.
2. **O item 19 também da pasta principal** (`D:\programas\EditorImpressao`): a linha do motor e a do Visual C++ têm de
   dizer as mesmas pastas da cópia (D-605: "da pasta principal, nada muda").
3. **O item 8 do roteiro ainda diz** `(conferido: "não existe")` para o `--apagar`; vale o item 18 ("foi apagada ...").
   Riscar o 8 para a gerente não ler as duas.

E o olhar da volta 9 (a data da pasta errada de 19/11 continua a mesma): hoje ela está em 19/11/2026 15:44.

## Para a gerente: o que ficou fora do projeto

Na pasta de rascunho desta conversa, em
`C:\Users\fotog\AppData\Local\Temp\claude\b9ca076ad002e817\14e42ebb-3236-41f4-94f5-20370c33bd91\scratchpad\quebra9\`
(pasta nova, criada nesta tarefa):

- `c21f1fc50\`, `c5c22a12d\`, `c011b06d0\`: o código desses commits (`git archive`, sem `relatorios`, `docs` e
  `memoria`; uns 19 MB cada). Na `c21f1fc50\` está o arquivo de testes do publicar de `011b06d0` por cima; na
  `c5c22a12d\`, os dois arquivos de teste, a peça do git e o repositório de prova de `011b06d0` por cima. A `c011b06d0\`
  está como saiu do git (as mutações foram desfeitas, conferido byte a byte).
- As sondas, o script das mutações e os resultados (os mesmos de `anexos-8/`), os dois registros das rodadas do GitHub
  (`log-*.txt`, ~0,9 MB cada) e `s6_saida.txt` (a saída da sonda S6).

Fora da pasta de rascunho: o pytest cria as pastas dele em `C:\Users\fotog\AppData\Local\Temp\pytest-of-fotog\` (ele
guarda só as últimas). A sonda S6 deixou o git esperando 15 s e depois o deixou terminar sozinho (fechando a entrada);
conferi que não sobrou nenhum `git.exe` aberto. Não apaguei nada em lugar nenhum.

`git -C D:\programas\EditorImpressao rev-parse --is-shallow-repository` = false. Nenhuma junção criada nem tocada; a
pasta errada de 19/11 e a `dist\` não foram tocadas.

## Fontes de fora

- Python 3.14, `Lib/subprocess.py`, função `run`, linhas 554 a 570 (lido no PC:
  `C:\Users\fotog\AppData\Local\Python\pythoncore-3.14-64\Lib\subprocess.py`).
- PyInstaller 6.21.0, `PyInstaller/lib/modulegraph/modulegraph.py`, linhas 920 a 935 (lido no `.venv`).
- Git for Windows 2.53.0: a recusa por dono diferente (vista rodando) e o lançador `cmd\git.exe` (o que o Windows acha
  pelo caminho de sempre, visto com `Get-Command git -All`).
- git-rev-parse, `--git-common-dir`, `--path-format` e `--local-env-vars`: https://git-scm.com/docs/git-rev-parse
  (citado pelo outro; conferi só o uso).
