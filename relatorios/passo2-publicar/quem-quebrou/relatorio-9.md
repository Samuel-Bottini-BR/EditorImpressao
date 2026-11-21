# Passo 2 do plano da parte do Windows: nona conferência de quem tentou quebrar (volta 10, 21/11/2026)

Sou um agente novo nesta volta (D-815). Não escrevi este código e não conferi as voltas anteriores. Não mexi no código
do outro: as minhas mudanças foram em cópias (`git archive`), na pasta de rascunho `quebra10\`.

O que **não** fiz:

- não rodei o publicar, o PyInstaller, o vpk nem o `gh release` de verdade (D-785, item 8: a gerente roda, à vista);
- não abri janela, console nem pergunta do Windows na tela do Samuel (todo Python e todo git abriram sem janela);
- não disparei rodada do GitHub (só consultei a 44869743074);
- não rodei o motor do Kraken de verdade nem `tests/test_ocr_kraken.py`; um Python por vez, um arquivo de teste por vez;
- não mexi em `C:\EditorImpressaoProva` (só listei), na pasta errada de 19/11 (só listei: a data continua
  19/11/2026 15:44:27) nem na junção `modelos`.

## Pedido

- Papel: quebrador
- Commit de partida: accafb80
- Ramo: passo2-publicar-2026-11-19

## Arquivos que vou mexer

- `core/pasta_das_ferramentas.py`
- `tests/test_pasta_das_ferramentas.py`
- `regras_dos_agentes/conversa_com_o_git.py`
- `regras_dos_agentes/repositorio_de_prova.py`
- `core/windows.py`
- `compilar_st_ferramentas.py`
- `publicar_versao_kaique.py`
- `empacotar.py`
- `montar_motor_kraken.py`
- `compilar_detector_gravura.py`
- `core/ocr_kraken.py`
- `tests/test_empacotar.py`
- `tests/test_publicar_*.py`
- `tests/test_windows_peca.py`
- `tests/test_conferencias_*.py`
- `relatorios/passo2-publicar/`

(Só mexi de verdade em `relatorios/passo2-publicar/`: este relatório, `quem-quebrou/anexos-9/` e o pacote
`anexos/pacote-quem-quebra-volta10.md`, que a gerente deixou fora do git e vai no meu commit. Os outros arquivos da lista
só foram lidos, ou mudados em cópias à parte.)

## Veredito

**PRONTO PARA CONFERIR: a pasta das ferramentas agora é um caminho escrito num lugar só, e eu não consegui fazer
nenhum dos seis lugares procurar nem criar pasta em outro lugar, com o git funcionando, sem git ou com o git recusando.**
O defeito do relatório 8 (voltar calado à pasta errada quando o git não responde) deixou de existir: não há mais conta
nenhuma que possa errar. O programa do Kaique não muda.

Ficam 4 baixos e 6 observações (abaixo). Nenhum chega ao Kaique nem ao livro. O baixo 1 é do roteiro da prova à vista:
dois itens pedem para repetir "da pasta principal", e a pasta principal está no `fase-1`, que ainda não tem o publicar;
a gerente precisa acertar esses dois itens antes da prova. Nunca "aprovado": só o Samuel aprova.

O que está certo (provado rodando, não só lido):

- **Da cópia de trabalho de verdade (`passo2`), os seis lugares dão `D:\programas\EditorImpressao-arquivos\ferramentas`**,
  o motor achado é o de lá, "pode gravar" diz que pode, e o git nem é carregado (sonda S1).
- **A reversão confere com a do outro:** os 12 testes novos no código de `6fa766c4`: 10 falham e 2 passam (os do
  "empacotado" e do "sem janela", que cobram o que já existia); o da frase do apagar falha lá ("de a pasta").
- **As 9 conferências do porteiro passam no PC, um arquivo por vez**, e o repositório continua inteiro (não raso).
- **A rodada 44869743074 passou (success) sobre o código certo**: ela tirou `3529cf9c`, que tem o código de
  `09b30933` (de `09b30933` a `accafb80` só o formulário mudou); `test_pasta_das_ferramentas.py` 12, `test_publicar_versao.py`
  122, `test_empacotar.py` 42 e 1 pulado, `test_ocr_kraken.py` 27 e 6 pulados, as 9 conferências, o juiz do porteiro e os
  botões da janela real.
- **Os testes que saíram eram só desta tarefa:** os cinco que saíram e os dois que mudaram de nome nasceram no commit
  `cea2b486` (volta 9); o arquivo de testes nem existia antes do passo 2 (`03c91599`). Nos arquivos de teste antigos,
  a volta 10 só acrescentou um teste (`test_publicar_versao.py`) e mudou o texto de explicação de um teste da volta 9
  (`test_empacotar.py`). Nenhum teste que cobrava algo passou a cobrar menos.
- **Das minhas 8 mutações, as 4 que tentam trazer de volta o defeito foram acusadas** (o caminho escrito de novo em outro
  arquivo, em dois arquivos; o Kraken olhando a pasta do Samuel no programa empacotado; a frase que não diz onde
  procurou). As 4 que passam são dos baixos 3 e 4 e da observação 1.

## Decisões que esta tarefa precisa cumprir

Palavras copiadas do Livro (`obra-juncao`, `docs/plano/DECISOES.md`), e como as achei nesta entrega.

- **D-605** "A partir de agora, nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já está escolhido e testado, coisas novas não podem criar novos problemas, essa é uma nova regra que todos os agentes precisam ler"
  Aqui: **cumprida**. O programa do Kaique (empacotado) procura o motor primeiro ao lado dele e não olha a pasta das
  ferramentas (teste do outro, e a mutação V3 é acusada). Rodando pelas fontes, o programa acha o motor do Samuel (sonda
  S1: "motor do programa" = `D:\programas\EditorImpressao-arquivos\ferramentas\motor-kraken`; o defeito antigo nº 330
  não volta). Nenhum teste antigo mudou o que cobra. As 9 conferências do porteiro passam.
- **D-727** "pode, se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador né"
  Aqui: **cumprida** (não muda): o Visual C++ continua tirado de `ferramentas\downloads` e conferido pela assinatura.
- **D-767** "não faça mais nada escodindo ou de mentira" · "não quero fazer consertos quero que funcione" · "quero que faça as coisas certas e sem bugs ou erros, deveria ter pensado nesses erros na hora de montar a estrutura do atualizador e testes a distancias"
  Aqui: **cumprida**, com o baixo 2. Os testes rodam os scripts e o git de verdade, num repositório de prova com uma
  cópia de trabalho de verdade, com a pasta de prova longe do código. Mas a troca do caminho nos testes cai calada no
  caminho de verdade se a linha mudar de jeito (baixo 2).
- **D-775** "o agente vai tentar quebrar antes de fazer o teste real na tela né?" · "ok"
  Aqui: **cumprida** por este relatório. Nenhum grave nem médio: pode seguir para a prova à vista, depois de a gerente
  acertar os itens 19 e 21 do roteiro (baixo 1).
- **D-776** "Sim, no C só tem que cuidar para não encher o disco C inteiro"
  Aqui: não muda (a conta do espaço não foi tocada nesta volta).
- **D-785** "ok, mais ainda existem mais casos na opção A" · "ok"
  Aqui: **cumprida** por mim (nada à vista rodei).
- **D-788** "1" (a primeira opção)
  Aqui: **cumprida**. Empacotado, `pasta_das_ferramentas()` devolve None e a lista do motor fica com "ao lado do
  programa" primeiro. A peça do git fica fora do pacote pela lista de exclusão (só a linha de comando do PyInstaller é
  conferida por teste; o pacote montado, só o item 20 do roteiro mostra).
- **D-813** "ok" (a recusa e a procura comparam a coisa de verdade, não o texto)
  Aqui: **cumprida no que importa**: o lugar não depende mais de como a pasta do código é escrita (é uma linha fixa).
  Sobra uma comparação pelo texto nos três scripts que gravam ("é o caminho de fábrica?"): `..`, `\\?\` e
  `\\localhost\D$` dizem "não é" (sonda S2). Não faz mal (o caminho passado é o mesmo lugar), mas anoto (observação 2).
- **D-815** "pode conferir se não está ocorrendo alucinação por estar com contexto cheio" · "estou falando do agente que está trabalhando" · "esses agentes que você criou, sempre que vai fazer uma tarefa nova, chama outro com a mesmas instruções ou ifac rodando sempre o mesmo com memorias compactadas?" · "ok"
  Aqui: **cumprida**: sou agente novo nesta volta; o escritor da volta 10 era novo (o jeito A foi a segunda volta dele,
  então a próxima volta de conserto, se houver, vai para um escritor novo).
- **D-816** "A , mas onde estamos antes de você fazer qualquer processo"
  Aqui: não muda (só a frase do apagar ganhou a contração; as linhas que decidem o que se apaga não mudaram).
- **D-818** "vai ter que reprogramar?" · "A"
  Aqui: não muda (a conferência da pasta já montada não foi tocada).
- **D-819** "não era melhor só ver se está instaldo no pc?" · "porque você escolheu o jeito mais dificil e nem perguntou para mim?" · "nova regra, sempre se deve se ver se é a coisa mais simples, ou melhor de se fazer, tem vezes que o mais simples é melhor e tem vezes que o mais complicado é melhor"
  Aqui: **cumprida**. O jeito A é o mais simples que resolve, e o outro comparou os dois por escrito. Sobrou pouca
  complicação sem uso (observação 1): um ramo que nunca roda, um nome que só os testes usam, e um "pode gravar" escrito
  duas vezes (baixo 3).
- **D-820** "não era melhor só ver se está instaldo no pc?" · "a versão B é usada por quais app?" · "A" · "mas pera ai , o que os programadores senior recomendam em casos assim?"
  Aqui: **cumprida**, com uma ressalva. A pasta está escrita num lugar só; nada pergunta ao git; nada calcula pela pasta
  de cima do código (grep, abaixo); sem a peça, para e diz onde procurou; sem o motor, diz também "aponte-a com
  --motor-kraken <pasta>". A ressalva: para o Visual C++, sem a pasta das ferramentas, o empacotar e o publicar dizem onde
  procuraram, mas não há opção para apontar outro lugar (a frase diz "Rode no PC onde ela existe"; observação 3).

## O que li

- As regras do verificador (`.claude/agents/verificador.md`), o `CLAUDE.md` inteiro da cópia `passo2`, a memória
  (`memoria/INDICE.md`; `memoria/geral/atualizador.md` só existe na pasta principal, li lá; o catálogo dos erros da
  `obra-juncao`, as famílias F1 a F10) e o pacote `anexos/pacote-quem-quebra-volta10.md`.
- No Livro da `obra-juncao`, as linhas inteiras de D-605, D-727, D-767, D-775, D-776, D-785, D-788, D-813, D-815,
  D-816, D-818, D-819 e D-820. (O pacote diz "não achada" para D-813 a D-820: elas existem no Livro da `obra-juncao`,
  linhas 1103 a 1110. É o mesmo furo do pacote da volta 9.)
- O ONDE-PAREI do escritor: "Onde parei" e as partes Volta 10 de "Decisões", "O que já está escolhido", "Como fica", "A
  causa", "O que pode falhar", "O que li", "Testes", "Caminho e função", "Cada proteção", "Máquina ou olho",
  "Ressalvas", "Ideias e bugs", "Perguntas para o Samuel" e "A prova de verdade" (itens 1 a 22); os anexos
  `reversao-volta10-*`.
- O relatório 8 inteiro.
- O código: o diff inteiro de `6fa766c4` a `09b30933` (11 arquivos), `core/pasta_das_ferramentas.py` inteiro, o
  `tests/test_pasta_das_ferramentas.py` inteiro, a peça do git comparada com a de antes do passo 2 (`03c91599`), os
  `main` dos três scripts que gravam, `empacotar.preparar_vc_redist`, `achar_motor_kraken`, `juntar_pecas`,
  `publicar_versao_kaique.publicar_motor` e `Apagado`, e o `montar_motor_kraken.montar` e `_baixar_conferido`.
- **Peças de fora, lidas na fonte:** o `pyi-archive_viewer` do PyInstaller 6.21.0 (`.venv`,
  `PyInstaller/utils/cliutils/archive_viewer.py`, função `run`, linhas 221 a 268): `-l` lista, `-r` "Implies --list" e
  entra nos arquivos de dentro, `-b` só os nomes; o outro leu certo. O `pathlib` do Python 3.14 no Windows: a igualdade
  de dois caminhos ignora maiúsculas e o tipo da barra, mas não resolve `..`, `\\?\` nem `\\localhost\D$` (visto
  rodando, sonda S2). O nome curto de `D:\programas\EditorImpressao-arquivos\ferramentas`, pedido ao Windows
  (`GetShortPathNameW`), volta o nome longo: o D: não tem nomes curtos ligados.

## O que conferi nas falhas, nas peças de fora e nos caminhos

### A rodada do GitHub (consultada, não disparada)

- **44869743074: success**, de 05:12 (hora do GitHub) de 21/11. O registro cita `3529cf9c` 71 vezes; de `09b30933` a
  `accafb80` só `relatorios/passo2-publicar/ONDE-PAREI.md` mudou. Todos os trabalhos da rodada: success (os de
  velocidade, pulados, como sempre sem pedido).

### Sobrou algum lugar que procura ou cria a pasta por conta própria?

Busca (`git grep` em `09b30933`, fora de `tests/` e `relatorios/`) por `RAIZ.parent`, `parents[`, `parent.parent`,
`EditorImpressao-arquivos`, `"ferramentas"`, `pasta_principal`, `limite_s`:

- O caminho das ferramentas aparece em código **só** em `core/pasta_das_ferramentas.py:43`. Nos outros arquivos aparece
  em comentário e em texto de ajuda (`empacotar.py:1984`, `montar_motor_kraken.py:618`, os cabeçalhos dos scripts).
- `parent.parent` sobra em `core/ocr_kraken.py:144` (a raiz do código, para o lugar 2 do motor, que é dentro do
  código) e em lugares que acham `modelos\` ou o acervo (outra pasta). Nenhum acha as ferramentas.
- `pasta_principal`, `e_copia_de_trabalho` e `SemPastaPrincipal` não existem mais em lugar nenhum; ninguém chama
  `pasta_das_ferramentas(...)` com argumento (a assinatura mudou e todos os chamadores foram trocados).
- Importar o `empacotar` não faz mais nada no disco nem no git (antes, na volta 9, perguntava ao git ao carregar).

### O caminho escrito de outro jeito (D-813, sonda S2, anexo `sonda-s2.txt`)

| Jeito | Os scripts acham que é o de fábrica? | O mesmo lugar no disco? |
|---|---|---|
| minúsculas, barras `/`, barra no fim, `\.\` | sim | sim |
| `..`, `\\?\`, `\\localhost\D$` | **não** | sim |
| nome curto | (o D: não tem nome curto: volta o longo) | sim |

Quando o script acha que não é o de fábrica, ele não pergunta "pode gravar?" e grava no caminho passado. Como é o mesmo
lugar, nada vai para o lugar errado; e, se a pasta não existe, ele cria a pasta certa (a escolhida à mão). Observação 2.

### Sem a pasta ou sem a peça

| Caso | O que acontece | Certo? |
|---|---|---|
| Da cópia `passo2`, tudo no lugar | os seis lugares e os dois motores: `D:\programas\EditorImpressao-arquivos\ferramentas` (sonda S1) | sim |
| Da cópia e da principal, sem git, com o git recusando o dono | o mesmo (teste do outro, que roda o git de verdade; passou no PC e no GitHub) | sim |
| Sem a pasta das ferramentas: o `montar_motor_kraken`, os dois compiladores | param com "não existe a pasta das ferramentas ... nada foi criado" e a opção de apontar outro lugar (testes do outro) | sim |
| Sem a pasta: a montagem do Visual C++ (empacotar e publicar) | para com a mesma frase, mas sem opção de apontar outro lugar (não existe essa opção) | observação 3 |
| Sem o motor: o empacotar e o `publicar --motor` | "não existe <cada lugar>" e "aponte-a com --motor-kraken <pasta>" (lido: os dois mostram todas as linhas da busca única) | sim, mas nenhum teste passa pelos dois (baixo 4) |
| `EditorImpressao-arquivos` existe, `ferramentas` não, na montagem do Visual C++ | hoje para; a decisão é uma conta própria do empacotar, e a mutação V8 (olhar a pasta de cima) passa em todos os testes | baixo 3 |
| Um **arquivo** chamado `ferramentas` | "pode gravar" diz que não (é `is_dir`); a mutação V7 (`exists`) passa nos testes | observação 1 |
| Empacotado | None; o motor ao lado do programa; nada perguntado ao git | sim |

Nenhuma frase diz "deu certo" sem ter dado: "pode gravar" só diz que pode quando a pasta existe, e quem grava confere o
resto do jeito de antes (o download e a assinatura do Visual C++, o "Já existe" do motor).

### O que saiu da peça do git

Comparei a peça do git de agora com a de antes do passo 2 (`03c91599`): mudaram só duas coisas, o git aberto sem janela
de console e a função nova `criar_copia_de_trabalho` (só para os repositórios de prova). O limite de tempo e a lista de
variáveis, que a volta 9 tinha posto, saíram. **A ressalva do outro está certa:** o defeito do achado 2 do relatório 8
era um limite de tempo que não segurava; hoje nenhuma pergunta ao git tem limite, como antes do passo 2, então não há
limite que falhe. O porteiro continua sem limite, como sempre foi (a pergunta B da gerente). O "sem janela" não muda o
que o porteiro lê: a saída e o código de volta são os mesmos (as 9 conferências passam).

### A prova de reversão (anexo `reversao-no-codigo-antigo.txt`)

Os testes de `09b30933` no código de `6fa766c4`, numa cópia minha: **10 falham, 2 passam** em
`test_pasta_das_ferramentas.py`, igual ao anexo do outro. Os 2 que passam (o do programa empacotado e o do git sem
janela) cobram o que já existia na volta 9. Os de B1 a B4 falham lá por outro motivo (no código de antes a pasta
caía na que o jeito do git acharia, imitada no teste, e os scripts seguiam): eles não provam a reversão das próprias
proteções, mas as mutações S14 a S18 do outro provam. O `test_obs6` (a frase do apagar) falha lá com "foi apagada de a
pasta".

### As mutações minhas (anexo `mutacoes-v-resultado.txt`; script `mutacoes_v.py.txt`)

Diferentes das S1 a S18 e T1 a T17 do outro e das B, P, U, R, Y, Z, W de antes. Uma por vez, numa cópia de
`09b30933`, devolvida ao original (conferido pelo git: mesmo conteúdo do commit).

| | O que desliguei | Acusada? |
|---|---|---|
| V1 | o empacotar escreve o caminho de novo, por conta própria (uma cópia da linha, não uma conta) | sim |
| V2 | o compilador do st_ferramentas escreve o caminho de novo | sim |
| V3 | o Kraken lê a linha direto e, empacotado, olha a pasta do Samuel | sim |
| V4 | a busca do motor deixa de dizer onde procurou | sim |
| V5 | o empacotar deixa de mostrar a linha "aponte-a com --motor-kraken" | **não** |
| V6 | o `publicar --motor` deixa de mostrar essa linha | **não** |
| V7 | "pode gravar" aceita um arquivo chamado `ferramentas` (`exists` em vez de `is_dir`) | **não** |
| V8 | a montagem do Visual C++ olha a pasta de cima e cria a das ferramentas | **não** |

V1 e V2 são a gambiarra que a D-820 quer evitar (o mesmo caminho escrito em dois lugares): os testes pegam, porque a
pasta de prova fica longe do código e a troca é feita só na linha da regra. Bom desenho.

### O que já funcionava em volta (§11.8)

- As 9 conferências do porteiro, no PC, um arquivo por vez (anexo `conferencias-no-pc.txt`).
- `test_pasta_das_ferramentas.py` e `test_decisoes_atualizacao.py` no PC: passam.
- `git rev-parse --is-shallow-repository` = false, na cópia e na pasta principal, depois de tudo.

## Caminhos que o outro não listou

1. **A pasta principal de verdade não tem este código.** A pasta principal (`D:\programas\EditorImpressao`) está no ramo
   `fase-1`, que não tem `publicar_versao_kaique.py` nem `core/pasta_das_ferramentas.py`. O outro escreveu "da pasta
   principal ... nada muda" e pôs no roteiro dois itens para repetir lá (baixo 1). O teste do outro cobre a pasta
   principal num repositório de prova; a de verdade só depois de juntar.
2. **A troca do caminho nos testes quando a linha muda** (o "seguro mexer" do próprio texto da regra): a cópia do
   teste fica com o caminho de verdade, calada (baixo 2).
3. **A montagem do Visual C++ decide "pode gravar?" por conta própria** (baixo 3).
4. **A frase do motor pelos dois que a mostram** (o empacotar e o publicar): só a função de dentro é testada (baixo 4).

## Falhas não pensadas e resultado não conferido

- **O teste acredita que trocou (F1, F9):** a cópia do código nos testes só troca o caminho se achar a linha escrita
  exatamente como hoje; se não achar, segue calada com o caminho de verdade, e os testes que rodam os scripts passam a
  ler a pasta de verdade do Samuel (baixo 2).
- **Proteção ou caminho que nenhum teste percorre (F3, de novo neste passo):** V5, V6, V7 e V8.
- **Resultado não conferido:** nada achado. A frase "pode gravar" só diz sim com a pasta lá.

## As regras que conferi

- **§11.12.1, uma peça só:** a pasta das ferramentas tem um lugar só (grep acima). O "pode gravar?" tem dois: a regra e a
  conta própria da montagem do Visual C++ (baixo 3).
- **§11.12.2, nada dá como feito o que não conferiu:** cumprida (tabela acima).
- **§11.12.3, a lista das falhas:** feita pelo outro, e certa, menos o caso da linha que muda nos testes (baixo 2).
- **§11.12.4 e D-767, peça de mentira:** os testes usam o git e os scripts de verdade; o do "empacotado" troca
  `sys.frozen` e diz que é só a lógica (é). O pacote de verdade fica para o item 20.
- **§11.12.6 e D-813:** o outro leu o PyInstaller certo. O jeito de escrever o caminho só importa nos três scripts
  (observação 2).
- **§11.8 e D-605:** nenhum teste antigo mudou o que cobra; os que saíram eram da volta 9 desta mesma tarefa, por ordem
  da gerente e pela D-820.
- **§4.7, teste de reversão:** confere (refiz).
- **§10.5, docstring:** todo arquivo e função tocados têm. Um comentário diz mais do que é (observação 1).
- **D-819, o mais simples:** cumprida (acima).
- **§11.13 (perguntas ao Samuel):** a pergunta do limite de tempo é "para a gerente primeiro"; se for ao Samuel, precisa
  ser reescrita (observação 5).

## Achados

1. **BAIXO: dois itens do roteiro da prova à vista não dão para fazer como estão escritos.**
   - Onde: `relatorios/passo2-publicar/ONDE-PAREI.md:3472` ("A prova de verdade", Volta 10, item 19, a segunda metade:
     "Repetir o mesmo da pasta principal (`D:\programas\EditorImpressao`)") e `relatorios/passo2-publicar/ONDE-PAREI.md:3487`
     (item 21, "O item 15 também da pasta principal").
   - Provado: a pasta principal está no ramo `fase-1` (`git rev-parse --abbrev-ref HEAD` = `fase-1`, em `d2146513`), e o
     `fase-1` não tem `publicar_versao_kaique.py` nem `servidor_das_versoes.py` nem `core/pasta_das_ferramentas.py`
     (`git cat-file -e` falha nos três). Seguido ao pé da letra, o comando dá "arquivo não encontrado". Para fazer o
     item, seria preciso trocar o ramo da pasta principal, que é a cópia de trabalho do Samuel (o atalho de
     desenvolvimento roda de lá): isso mexe no que é dele (família F9).
   - O que falta não é grave: o caso "da pasta principal" está provado pelo teste do outro, num repositório de prova
     com a pasta principal e uma cópia de trabalho de verdade; e, com o caminho escrito, rodar de um lugar ou de outro
     não muda a conta.
   - Eu pedi isso no relatório 8 ("O item 19 também da pasta principal") sem ver que a principal está no `fase-1`. O erro
     começa aqui.
   - O que pedir: reescrever os itens 19 e 21: agora, só da cópia `passo2`; "da pasta principal" fica para depois de o
     trabalho entrar no `fase-1` (a gerente repete lá na junção, sem trocar ramo nenhum).

2. **BAIXO: a troca do caminho nos testes cai calada no caminho de verdade quando a linha muda.**
   - Onde: `tests/test_pasta_das_ferramentas.py:83-101` (`_copiar_o_codigo`: `if texto.count(LINHA_DO_CAMINHO) == 1:`
     troca; senão, segue sem trocar) e `:61` (`LINHA_DO_CAMINHO`).
   - Provado (sonda S3, anexo `sonda-s3.txt`, só a cópia, nenhum script rodado): com a linha mudada do jeito que o
     próprio texto da regra chama de "seguro mexer" (a pasta mudou de lugar: `E:\programas\...`), a cópia de prova do
     teste fica com `PASTA_DAS_FERRAMENTAS = Path(r"E:\programas\EditorImpressao-arquivos\ferramentas")`, o caminho de
     verdade. (Um comentário no fim da linha ainda é trocado certo.)
   - O que acontece então (lido, não rodado): o teste que confere a linha falha com a frase certa ("troque também
     LINHA_DO_CAMINHO"), mas os outros testes do mesmo arquivo continuam e rodam os scripts de verdade contra a pasta de
     verdade do Samuel. Pelo que li, hoje nada seria gravado lá: o `montar_motor_kraken` para em "Já existe ..." (o
     motor está lá), os downloads já estão lá, e a internet fica trancada no processo. Mas isso é acaso, não proteção. No
     Windows do GitHub não acontece (lá a pasta não existe).
   - O que pedir: quando a regra existe e a linha não é achada, o teste parar na hora (`pytest.fail`) em vez de seguir;
     ou trocar pela atribuição (`PASTA_DAS_FERRAMENTAS = ...`, qualquer que seja o caminho) e conferir, na cópia, que o
     caminho ficou o de prova antes de rodar qualquer script.

3. **BAIXO: a montagem do Visual C++ decide "pode gravar?" por uma conta própria, e nenhum teste a acusa.**
   - Onde: `empacotar.py:666-668` (`if not DOWNLOADS.parent.is_dir(): return ... [_pasta_das_ferramentas.problema_para_gravar() or f"não existe a pasta ..."]`).
   - Lido: quem decide é o `DOWNLOADS.parent.is_dir()` do próprio empacotar; a regra (`problema_para_gravar`) só dá as
     palavras, e há uma segunda frase para quando as duas discordam. Hoje dão o mesmo (as duas olham a mesma pasta). O
     "caminho → função" do outro diz que este "pode gravar?" usa `problema_para_gravar()` (§11.12: "uma regra, um lugar
     só").
   - Provado (mutação V8): olhar a pasta de cima e criar a das ferramentas, aqui, passa em `test_pasta_das_ferramentas.py`
     e `test_empacotar.py`. É a B5 do relatório 8, que foi consertada só na regra.
   - O que pedir: o empacotar perguntar à regra (`problema = problema_para_gravar(); if problema: return ...`), sem a
     conta nem a frase próprias; e um teste da montagem do Visual C++ com `EditorImpressao-arquivos` existindo sem
     `ferramentas` dentro.

4. **BAIXO: a frase "aponte-a com --motor-kraken" não é testada por quem a mostra.**
   - Onde: `empacotar.py:707` (`juntar_pecas`) e `publicar_versao_kaique.py:1120` (`publicar_motor`).
   - Provado (mutações V5 e V6): tirar essa linha só no empacotar, ou só no publicar, passa em
     `test_pasta_das_ferramentas.py`, `test_empacotar.py` e `test_publicar_versao.py`. O teste do outro lê a função de
     dentro (`achar_motor_kraken`), não o que o Samuel vê.
   - Lido: hoje os dois mostram todas as linhas da busca, então a frase aparece nos dois. É a família F3 outra vez
     neste passo (§11.12: "uma prova que passa pelos caminhos principais").
   - O que pedir: um teste pelo `publicar --motor` (o `Parou` que ele levanta) e um pelo empacotar (o que ele imprime),
     sem motor, cobrando "onde procurou" e "--motor-kraken".

5. **OBSERVAÇÃO 1 (D-819): sobras pequenas.**
   - `core/pasta_das_ferramentas.py:68-69`: o ramo "o programa empacotado não tem a pasta das ferramentas" de
     `problema_para_gravar` nunca roda (ninguém que grava roda empacotado).
   - `core/pasta_das_ferramentas.py:44`: `NOME_DA_PASTA_DO_SAMUEL` diz "(as frases e os testes o usam)"; só os testes
     usam.
   - `empacotar.py:667-668`: a segunda frase (`or f"não existe a pasta ..."`) só aparece se as duas contas discordarem
     (baixo 3).
   - `core/pasta_das_ferramentas.py:70` (mutação V7): um arquivo chamado `ferramentas` no lugar da pasta não tem
     teste. Hoje está certo (`is_dir`).
   - `tests/test_pasta_das_ferramentas.py:212-221`: a armadilha "a regra não pergunta ao git" já não pode disparar (a
     regra nem importa a peça do git). Não faz mal; prova pouco.

6. **OBSERVAÇÃO 2 (D-813): "é o de fábrica?" nos três scripts compara o texto.**
   - Onde: `montar_motor_kraken.py:637`, `compilar_detector_gravura.py:284-285`, `compilar_st_ferramentas.py:212-213`.
   - Sonda S2: `..`, `\\?\` e `\\localhost\D$` dizem "não é o de fábrica"; aí o script grava no caminho passado sem
     perguntar "pode gravar?". É o mesmo lugar, então não faz mal. Anoto pela D-813.

7. **OBSERVAÇÃO 3 (D-820): para o Visual C++ não há "como apontar outro lugar".**
   - Onde: `empacotar.py:666-668` e `core/pasta_das_ferramentas.py:71-72` ("Rode no PC onde ela existe").
   - Sem a pasta das ferramentas, o empacotar e o publicar dizem onde procuraram, mas não há opção para o Visual C++ (os
     scripts têm `--destino`, `--downloads`, `--ferramentas`; o empacotar e o publicar não). O "Como fica" do outro diz
     "e a opção do script para apontar outro lugar"; vale para os três scripts, não para o empacotar. Criar a opção seria
     coisa nova (§11.7): não peço; anoto para a gerente decidir se a frase basta.

8. **OBSERVAÇÃO 4: os comandos do roteiro começam por `.venv\Scripts\...`.**
   - Onde: `relatorios/passo2-publicar/ONDE-PAREI.md:3379` (item 1) e `relatorios/passo2-publicar/ONDE-PAREI.md:3481`
     (item 20).
   - A cópia `passo2` não tem `.venv` (ela está na pasta principal: `D:\programas\EditorImpressao\.venv\Scripts\`; o
     `pyi-archive_viewer.exe` existe lá). Escrever o caminho inteiro.

9. **OBSERVAÇÃO 5 (§11.13): a pergunta do limite de tempo do porteiro usa palavras de dentro.**
   - Onde: `relatorios/passo2-publicar/ONDE-PAREI.md:3096` ("Perguntas para o Samuel", Volta 10).
   - Usa "porteiro", "juiz", "peça do Windows", "rodada do GitHub". Ela está marcada "para a gerente primeiro"; se for ao
     Samuel, precisa ser reescrita. A sugestão A ("deixar como está") é a que não muda nada.

10. **OBSERVAÇÃO 6: o git sem janela continua valendo para o porteiro** (a observação 10 do relatório 8 continua).
    - Onde: `regras_dos_agentes/conversa_com_o_git.py:32` e `regras_dos_agentes/conversa_com_o_git.py:48`.
    - Um git que precisasse pedir usuário e senha no terminal não pede (falha ou espera sem ninguém ver). Dedução; hoje o
      porteiro não pede senha, e as 9 conferências passam.

## O que falta para a prova à vista

O roteiro do outro (itens 18 a 22) basta para a gerente repetir com o Samuel só o que mudou, em uns 10 minutos, com
três acertos:

1. **Itens 19 e 21: só da cópia `passo2`** (baixo 1). "Da pasta principal" fica para a junção.
2. **Os comandos com o caminho inteiro do `.venv`** (observação 4).
3. **O olhar da pasta errada de 19/11:** hoje `D:\programas\EditorImpressao\.claude\worktrees\EditorImpressao-arquivos\`
   está com 19/11/2026 15:44:27 (a pasta e a `ferramentas`), a `downloads` com 15:44:29 e o `vc_redist.x64.exe` com
   25.635.768 bytes, de 15:44:28. Depois da prova, tem de estar igual.

O item 22 dá para fazer como está (lido: com uma pasta que não existe, o `publicar --motor` para com "não achei um
motor pronto do jeito novo: não existe <a pasta>"). As pastas `versoes 3`, `versoes 4` e `versoes 5` ainda não existem em
`C:\EditorImpressaoProva` (só listei).

## Para a gerente: o que ficou fora do projeto

Na pasta de rascunho desta conversa, em
`C:\Users\fotog\AppData\Local\Temp\claude\b9ca076ad002e817\14e42ebb-3236-41f4-94f5-20370c33bd91\scratchpad\quebra10\`
(pasta nova, criada nesta tarefa):

- `antigo\` e `novo\`: o código de `6fa766c4` e de `09b30933` (`git archive`, sem `relatorios`, `docs` e `historico`;
  uns 21 MB cada). Em `antigo\tests\` estão por cima os dois arquivos de teste de `09b30933`
  (`test_pasta_das_ferramentas.py` e `test_publicar_versao.py`). A `novo\` está como saiu do git (as mutações e a sonda
  S3 foram desfeitas; conferido pelo git).
- `s3-comentario-no-fim\` e `s3-a-pasta-mudou-de-lugar\`: as duas cópias que a sonda S3 montou com a função do teste
  (só arquivos `.py` e `.txt`).
- Os scripts e os resultados (os mesmos de `anexos-9/`) e o registro da rodada 44869743074 (`rodada-44869743074.log`,
  ~0,9 MB).

Fora da pasta de rascunho: o pytest cria as pastas dele em `C:\Users\fotog\AppData\Local\Temp\pytest-of-fotog\` (ele
guarda só as últimas). Não apaguei nada em lugar nenhum. `git rev-parse --is-shallow-repository` = false na cópia e na
pasta principal. Nenhuma junção criada nem tocada; a pasta errada de 19/11, a `dist\` e `C:\EditorImpressaoProva` não
foram tocadas.

## Fontes de fora

- PyInstaller 6.21.0, `PyInstaller/utils/cliutils/archive_viewer.py`, função `run`, linhas 221 a 268 (lido no `.venv`).
- Python 3.14, `pathlib` no Windows: a igualdade de caminhos, vista rodando (sonda S2); `os.path.samefile` para o "mesmo
  lugar".
- Windows, `GetShortPathNameW` (kernel32), chamado só para ler o nome curto.
