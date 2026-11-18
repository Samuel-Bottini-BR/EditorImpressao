# Publicar uma versão para o Kaique: por que leva quase 1 hora, e como deixar rápido

Estudo do pesquisador, 18/11/2026. Nenhuma linha do programa, dos scripts de publicar ou dos testes mudou.
Ramo `publicar-rapido-2026-11-18`. Medidas feitas das 12:06 às 13:32, com a etapa 5 já terminada.

## A resposta, em poucas frases

1. **Publicar demora por causa do disco, não do processador.** A cada versão, a ferramenta (o Velopack) copia a
   pasta do programa inteira quatro vezes, comprime três vezes e, para fazer a diferença, abre de novo duas versões
   inteiras. Tudo isso no **HD externo** (o D:, ligado por USB).
2. **Quase todos os arquivos são do motor do Kraken:** 34.521 dos 35.103 (98%). Ele nunca muda, mas é copiado e
   comprimido de novo toda vez. Num HD, é a quantidade de arquivos que pesa.
3. **Medido:** a mesma diferença leva **20,5 min no D: e 3,6 min no C:** (o disco de dentro, um SSD). O pacote
   inteiro, sem instalador, leva **7,6 a 8,4 min** com o trabalho no C:. Hoje, no D: e com tudo junto, o Velopack
   leva de 50 a 72 min.
4. **Duas mudanças no jeito de publicar cortam a maior parte do tempo:** fazer o trabalho no C:, e só refazer o
   instalador (o .msi) quando o Samuel pedir. Publicar cai de **70 a 93 min** para uns **24 a 32 min**, contando os
   ~10 min de montar a pasta do programa (medido por partes).
5. **No PC do Kaique, a atualização "pequena" é a mais lenta.** Ele baixa uns 20 MB, mas o computador remonta o
   pacote inteiro antes de trocar: **22 a 23 min**, contra **7,5 min** quando vem o pacote inteiro (medido no
   registro da atualização da etapa 5).
6. **Achado de segurança (lido no código, não provado em teste):** pelo caminho da diferença, a assinatura do PC do
   Samuel não confere o que é instalado. Ela confere só o pacote inteiro.
7. **Publicar sem diferença** resolve o 5 e o 6, e tira mais uns 4 min do publicar (cerca de **21 a 28 min** no
   total). O custo é o Kaique baixar 826 MB por versão. Isso é escolha do Samuel (pergunta 3), porque ele escolheu o
   Velopack justamente por "baixar só o que mudou".

## 1. Onde vai cada minuto hoje (medido nos registros da etapa 5)

Tempos tirados dos horários dos registros `saida_teste/etapa5/registros/publicar-1.1.0.log` e
`fase1-resto-limpo.log` (Velopack 1.2.161, tudo no D:). Nas versões 1.1.1 a 1.1.5 o programa era **o mesmo**:
só o número da versão mudou.

| Passo | 1.1.1 | 1.1.2 | 1.1.3 | 1.1.4 | 1.1.5 | O que é |
|---|---|---|---|---|---|---|
| Baixar a versão anterior | 0:19 | 0:41 | 0:34 | 0:32 | 0:27 | cópia do servidor de mentira |
| Pré-processo | 3:27 | 5:51 | 10:00 | 6:10 | 5:36 | 1ª cópia da pasta (35 mil arquivos) |
| Pacote completo + portátil (juntos) | 12:05 | 16:29 | 12:28 | 18:52 | 21:57 | 2ª e 3ª cópias, duas compressões ao mesmo tempo |
| Setup.exe | 0:31 | 0:45 | 0:30 | 2:04 | 0:46 | junta o pacote completo a um .exe |
| .msi: cópia | 6:57 | 11:10 | 8:05 | 11:04 | 15:17 | 4ª cópia da pasta |
| .msi: montar (WiX) | 26:13 | 26:42 | 24:47 | 24:37 | 27:45 | 3ª compressão, ao mesmo tempo que a diferença |
| Diferença ("só o que mudou") | 28:11 | 33:16 | 30:04 | 33:20 | 37:25 | abre os dois pacotes, compara, apaga |
| Fim do Velopack | 0:48 | 0:41 | 0:37 | 0:40 | 0:33 | |
| **Velopack, total** | **50:02** | **61:42** | **56:30** | **63:29** | **71:58** | |
| Do fim do Velopack ao envio | 5:14 | 7:09 | 5:09 | 4:22 | 5:30 | ver nota |
| Copiar para o servidor | 3:37 | 3:34 | 3:38 | 3:34 | 3:39 | 3,2 GB (completo, portátil, Setup, .msi) |
| **Total da versão** | **59** | **73** | **66** | **72** | **82** min | sem contar os ~10 min de montar a pasta |

O que se vê:

- **A diferença e o .msi rodam juntos e disputam o mesmo HD.** Na 1.1.0, com o .msi sozinho, o WiX levou 13 min.
  Nas outras, com a diferença rodando junto, levou de 25 a 28 min. Sozinha no D:, a diferença leva 20,5 min (M4).
- **Uns 7 min da "diferença" são só para apagar** os arquivos que ela mesma abriu (do "Delta processed" ao
  "Complete"). A M4 repetiu isso: 7 min 04 s apagando.
- **Os 4 a 7 min "do fim do Velopack ao envio" não são o nosso conferir e assinar.** Medido: conferir o pacote e
  calcular a soma da assinatura leva 1,5 s no C: e 21 s no D:. **Dedução:** o resto é o Velopack apagando as quatro
  cópias temporárias (uns 140 mil arquivos) depois de escrever "Finished". No C:, com duas cópias, isso levou
  24 a 33 s (M2a, M2b).
- **Fica mais lento a cada versão** (59 → 82 min). O pré-processo, que é só uma cópia, foi de 3,5 para 10 min.
  **Não medido:** combina com um HD que vai enchendo e se espalhando.

### Do que é feita a pasta do programa (medido no pacote 1.1.5 do servidor, só lendo)

| Parte | Arquivos | Tamanho | Comprimido |
|---|---|---|---|
| motor do Kraken | 34.521 | 1.090 MB | 341 MB |
| o programa (PyInstaller, `_internal`) | 539 | 600 MB | 308 MB |
| Tesseract | 36 | 177 MB | 83 MB |
| o .exe e soltos | 5 | 27 MB | 23 MB |
| Visual C++ (`instalar\`) | 2 | 24 MB | 24 MB |
| **total** | **35.103** | **1.918 MB** | **779 MB** |

### Os discos deste PC (medido)

- O C: é um SSD NVMe de 512 GB (WD SN530), com 26 a 28 GB livres hoje.
- O D: é um HD externo USB de 2 TB (WD easystore), com 182 GB livres.
- O processador é um Ryzen 7 5800H (8 núcleos, 16 linhas), com 15 GB de memória.
- Na etapa 5, o TEMP do publicar estava desviado para `saida_teste\etapa5\temp`, no D:.

## 2. Por que é assim (lido no código do Velopack 1.2.161, licença MIT)

Fonte: `github.com/velopack/velopack`, etiqueta `1.2.161` (commit `92d6a1c9`, 29/09/2026), copiada em
`saida_teste/publicar-rapido/fonte-velopack/repo`. Arquivos lidos: `src/vpk/Velopack.Packaging/PackageBuilder.cs`,
`PackOptionsValidator.cs`, `src/vpk/Velopack.Packaging.Windows/Commands/WindowsPackCommandRunner.cs`,
`src/vpk/Velopack.Packaging/Compression/DeltaPackageBuilder.cs`, `src/lib-csharp/Util/EasyZip.cs`,
`src/lib-csharp/Util/TempUtil.cs` e `src/vpk/Velopack.Packaging.Windows/Msi/`.

- **Pré-processo** (`PreprocessPackDir`): copia a pasta inteira para `%TEMP%\velopack\...`, arquivo por arquivo.
- **Pacote completo** (`CreateReleasePackage`): copia **de novo** para outra pasta temporária e comprime num zip. A
  compressão usa um processo só, no nível "Optimal", escrito fixo no código; não há opção para mudar.
- **Portátil** (`CreatePortablePackage`): copia **de novo** e comprime outro zip, ao mesmo tempo que o completo.
- **Setup.exe**: copia o pacote completo (826 MB) para dentro de um .exe. Leva 2 s no C:.
- **.msi**: copia a pasta **pela quarta vez**, e o WiX comprime tudo dentro do .msi. O .msi leva os arquivos do
  programa soltos, não o pacote.
- **Diferença** (`DeltaPackageBuilder`): descompacta **os dois pacotes inteiros** (uns 70 mil arquivos) e compara
  cada arquivo byte a byte. Para cada arquivo igual, grava **dois arquivos vazios** de marcação. Só o arquivo que
  mudou passa pelo Zstandard, que é onde entra o modo (BestSpeed ou BestSize). No fim, comprime tudo e apaga as
  pastas.
- Tudo vai para `%TEMP%\velopack` (`TempUtil`). Por isso, desviar o TEMP muda o disco de todo esse trabalho.
- As opções escondidas (`vpk pack -H`) são `--noInst` (sem Setup.exe e sem .msi), `--noPortable` (sem portátil) e
  `--delta None|BestSpeed|BestSize`. **Medido:** a 1.2.161 **recusa `--noInst` e `--noPortable` juntos** ("Cannot
  use 'noPortable' and 'noInst' options together", `PackOptionsValidator.cs`). O `--msi` não vem ligado de fábrica:
  nós o ligamos (`empacotar.comando_do_vpk`). Para uma versão de atualização, a combinação possível é
  **`--noPortable` sem `--msi`**: sai só o pacote e um Setup.exe (2 s).

**Disco, processador ou compressão (medido):**

| Trabalho | No D: (HD) | No C: (SSD) | Pesa o quê |
|---|---|---|---|
| Copiar a pasta inteira (35.100 arquivos, 2 GB), D: → C: | — | 2 min 07 s (M1) | ler do HD |
| Pré-processo (1ª cópia) | 3,5 a 10 min (etapa 5); 2 min 31 s a 8 min 31 s lendo do D: (M2a, M5b) | 36 s (M2b) | disco |
| Pacote completo (cópia + compressão) | 12 a 22 min, junto com o portátil (etapa 5) | 5 min 47 s a 6 min 58 s (M2a, M2b, M5b) | compressão (processador): quase igual nos dois discos |
| Diferença | 20 min 33 s, sozinha (M4) | 3 min 37 s (M3) | disco |
| Apagar o que a diferença abriu | 7 min 04 s (M4) | 45 s (M3) | disco |
| Conferir e calcular a soma da assinatura | 21 s (M4) | 1,5 s (M2a) | disco |

Então: quase tudo é **disco**, e o C: resolve. Sobra a **compressão do pacote completo**, uns 6 min, que é
processador e não tem opção para acelerar. **Não medido:** o antivírus também lê cada arquivo novo. Isso explica o
pré-processo de 8,5 min da M5b, que leu uma pasta recém-montada; a mesma cópia, lendo uma pasta antiga, levou 2,5 min.

**A diferença tem ~20 MB, mas o que mudou de verdade é muito menos (medido, só lendo os pacotes):**
- **Mesma pasta, só o número da versão mudou** (servidor 1.1.5, e a M3): 70.210 entradas, das quais só 6 têm
  conteúdo, uns 140 KB somados. O resto são as entradas vazias de "não mudou", e cada uma ocupa uns 280 bytes de
  cabeçalho no zip. Tamanho: 18,6 a 19,5 MB.
- **Pasta montada de novo pelo PyInstaller** (M5, M5b): 21,1 MB. O remendo do `EditorImpressao.exe` tem 116 bytes.
  Duas bibliotecas (`libcrypto`, `libssl`) entraram inteiras, uns 2,6 MB. **Dedução:** o PyInstaller pegou outra
  cópia delas do `.venv` nesta montagem.
- **BestSpeed e BestSize deram o mesmo tamanho (18,6 MB) e o mesmo tempo (3,6 min)** (M3). Só um arquivo pequeno
  mudou, e o modo só age nele.

## 2b. O lado do Kaique: quanto ele baixa e quanto tempo a troca leva

Medido no registro da atualização da etapa 5 (`C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log`, só
lido), no PC do Samuel. O programa estava instalado no C: e as versões vinham de uma pasta no D:.

| Versão | Caminho | "Baixando" (do registro) | Trocar e conferir | Total |
|---|---|---|---|---|
| 1.1.0 → 1.1.1 | pacote inteiro (826 MB) | 17 s (09:07:22 a 09:07:39) | 7 min 15 s (09:27:17 a 09:34:32) | ~7,5 min |
| 1.1.1 → 1.1.2 | diferença (19,5 MB) | 14 min 56 s (09:36:40 a 09:51:36) | 7 min 53 s (até 09:59:29) | ~23 min |
| 1.1.2 → 1.1.3 | diferença (19,5 MB) | 14 min 21 s (10:00:18 a 10:14:39) | 7 min 49 s (o teste rápido recusou, como devia) | ~22 min |

**Por que (lido no código do Velopack, `src/lib-rust/src/manager.rs` e `src/bins/src/commands/patch.rs`):**

- A **primeira** atualização depois do .msi vem sempre pelo pacote inteiro. O .msi não deixa o pacote da versão
  instalada na pasta `packages`, e sem ele a diferença não tem de onde partir (`create_delta_update_strategy`: "no
  local/base package available").
- **Pela diferença**, o "baixando" inclui remontar o pacote inteiro. O Velopack descompacta o pacote anterior inteiro
  (35 mil arquivos), aplica a diferença e **comprime tudo de novo** num pacote de 840 MB (`patch.rs`, `delta`). O
  remontado da 1.1.3 ficou com 839.424.186 bytes; o publicado tem 826.530.083. Baixar os 19,5 MB é o de menos.
- **A troca** (`apply_windows_impl.rs`) descompacta o pacote inteiro mais uma vez, troca as pastas e apaga a velha:
  de novo 35 mil arquivos, cada um lido pelo antivírus. Depois vem o nosso teste rápido.
- Então a diferença **economiza internet, mas custa uns 15 min a mais de trabalho do computador**. No notebook do
  Kaique (i5-1235U) deve ser parecido ou mais lento **[não medido]**.

**Quanto ele baixa de verdade:** pela diferença, uns 20 MB por versão (M5b: 21,1 MB). Pelo pacote inteiro,
826 MB. Na primeira atualização depois de instalar, sempre o inteiro.

### Achado de segurança: a diferença não passa pela assinatura (lido no código, não provado em teste)

- **O que a assinatura cobre hoje** (`atualizacao._versao_assinada_do`): o nome do pacote, a versão, o nome do
  arquivo do pacote **inteiro** e a soma dele. O programa confere isso **antes de baixar** (D-724).
- **Pelo caminho da diferença**, o Velopack confere a diferença baixada contra a soma escrita no arquivo de versões
  do servidor (`releases.win.json`), que **não é assinado** (`verify_package_checksum` em
  `download_and_apply_delta_updates`). Depois ele monta o pacote novo e **não o compara com a soma assinada**: o
  `patch.rs` pula as somas ("skip shasum files"), e o remontado nem tem o mesmo tamanho do publicado.
- **Consequência (dedução):** quem conseguisse trocar os arquivos de uma versão no GitHub (por exemplo, com a conta
  ou o token do Samuel) poderia publicar uma diferença adulterada. A assinatura verdadeira do pacote inteiro
  continuaria lá. A D-724 diz que "versão sem a assinatura certa não é instalada", e pelo caminho da diferença isso
  não está garantido.
- **O que foi provado na etapa 5:** a 1.1.4, com assinatura de chave falsa, foi recusada. Essa prova é sobre a
  assinatura do pacote inteiro. Uma diferença adulterada com a assinatura certa nunca foi testada.
- **Saídas:**
  (a) publicar **sem diferença**: o programa sempre baixa o pacote inteiro, conferido pela soma assinada. Nada muda
  no programa, só uma opção no comando do publicar.
  (b) manter a diferença e **assinar também a diferença**: o publicar põe a soma dela na assinatura, e o programa
  confere antes de baixar. É mudança no programa (`assinatura.py`, `atualizacao.py`), e pela D-765 espera a entrega.
  (c) desligar a diferença no próprio programa (`MaximumDeltasBeforeFallback`, opção do Velopack). Também é mudança
  no programa.
- **Limpa ou remendo:** a (a) e a (b) são limpas. A (b) mora num lugar só (`_versao_assinada_do` e
  `assinatura.VersaoAssinada`). A (c) deixaria publicadas diferenças que ninguém usa.

## 3. Cada saída possível

Para cada uma: quanto economiza, o que muda para o Kaique, a segurança (a assinatura, D-724), a etapa 5, e se é
solução limpa ou remendo (CLAUDE.md §11.12).

### 3.1 Fazer o trabalho do Velopack no C: (SSD) em vez do D: (HD externo)

- **Economiza (medido):** o pré-processo cai de 3,5–10 min para 0,6–2,5 min. A diferença cai de 20,5 min (sozinha)
  ou 28–37 min (junto com o .msi) para 3,6 min. A limpeza depois de cada passo cai de minutos para segundos.
- **Para o Kaique:** nada muda. **Medido:** o pacote montado no C: (M2a) tem exatamente o mesmo tamanho do publicado
  na etapa 5 (826.530.083 bytes).
- **Assinatura:** igual. Ela é feita depois, sobre o pacote pronto.
- **Etapa 5:** não é tocada.
- **Espaço no C: (medido pelo pico):** 5,3 a 6,1 GB para montar o pacote, sem diferença. Com a diferença, o pico
  estimado é de uns 10 GB: a M3 mediu 4 GB a mais para ela, e no publicar de verdade as duas partes ficam no disco ao
  mesmo tempo. Tudo é apagado no fim. O C: tinha 26 GB livres às 12:06, e caiu para 9,9 GB às 13:32 por outra
  coisa (ver seção 7). Com pouco espaço, o publicar teria de conferir o espaço antes de começar.
- **Limpa ou remendo:** limpa, se feita num lugar só.
  - Hoje o rascunho mora em `publicar_versao_kaique.PASTA_DE_TRABALHO` (`build\publicar`, ao lado do código, no D:).
  - O TEMP vem de quem chama: a etapa 5 o desviou à mão no `fase1_resto.ps1`.
  - O vpk é chamado por **dois caminhos**: `publicar_versao_kaique.publicar` (com `--pasta-pronta`, por `_rodar`) e
    `empacotar.construir_pacote_do_velopack` (por `subprocess.run`). Os dois usam a mesma regra do comando
    (`empacotar.comando_do_vpk`), mas cada um roda o processo do seu jeito.
  - O conserto limpo é **uma** função que roda o vpk com a pasta de trabalho e o TEMP certos, chamada pelos dois
    caminhos. Desviar o TEMP só num deles seria remendo.

### 3.2 Não gerar o .msi nem o portátil nas versões de atualização

- **O que dá para fazer na 1.2.161 (medido):** `--noPortable`, sem `--msi`. O Setup.exe continua saindo, mas leva
  2 s para fazer.
- **Economiza:** no D:, a 4ª cópia mais o WiX (33 a 43 min que hoje correm junto com a diferença e a atrasam), a 3ª
  cópia e uma compressão (o portátil). No C:, o pacote sozinho fica em **7,6 a 8,4 min** (M2a, M2b). O .msi e o
  portátil no C: não foram medidos: faltava espaço no limite de 8 GB.
- **Envio:** cada versão hoje sobe 3,2 GB (completo, portátil, Setup e .msi). Com a 3.2, sobem uns 1,7 GB (completo
  e Setup.exe), mais a diferença se houver. O Setup.exe (837 MB) continua subindo, porque a 1.2.161 não deixa tirar
  os dois.
- **Para o Kaique:** a atualização é igual. Ela usa só o pacote completo e a diferença, não o instalador (lido em
  `atualizacao.procurar_e_preparar` e em `lib-rust/src/manager.rs`). Muda só uma coisa: numa **instalação nova**
  (outro computador, ou reinstalar), o .msi disponível é o da última versão que o gerou. O programa instalado por
  ele se atualiza sozinho na primeira abertura (D-732).
- **Assinatura:** igual. O que se assina é o pacote completo, que continua saindo sempre.
- **Desinstalar:** quem desinstala é o .msi da **primeira** instalação, que o Windows guarda. O que foi provado em
  17/11 (D-763/D-764, Velopack 1.2.161) continua valendo.
- **Versão portátil (D-300, "Instalador em português, com desinstalador e versão portátil"):** a versão portátil do
  nosso programa é a pasta que o `empacotar.py --modo pasta` monta, e ela continua existindo. O zip portátil do
  Velopack é outra, que a etapa 5 nem usou. Mesmo assim, tirá-lo muda o que sai do publicar: vai na pergunta 2.
- **Limpa ou remendo:** limpa. A regra do comando já mora num lugar só (`empacotar.comando_do_vpk`): basta uma
  escolha "com instalador", ligada de fábrica como hoje, e uma opção no publicar para desligá-la. Com a escolha
  ligada de fábrica, o teste antigo
  `tests/test_decisoes_atualizacao.py::test_d727_o_vpk_nao_baixa_nada_na_hora_de_instalar` (que cobra o `--msi`)
  continua valendo sem mudar. Seria preciso um teste novo para o caminho "sem instalador".

### 3.3 O modo da diferença (None, BestSpeed, BestSize)

- **Medido (M3):** BestSpeed e BestSize deram o mesmo tempo (3 min 37 s e 3 min 33 s, no C:) e o mesmo tamanho
  (18,6 MB). O modo só age no arquivo que mudou de verdade. A documentação (`docs/packaging/deltas.mdx`) diz que o
  BestSize é "a lot slower" quando muda muita coisa.
- **None (sem diferença):** tira do publicar a diferença (3,6 min no C:, 20,5 a 37 min no D:) e o "baixar a versão
  anterior", que no GitHub de verdade é baixar 826 MB.
  - No PC do Kaique, tira os ~15 min de remontar o pacote: a atualização fica em ~7,5 min mais o tempo de baixar.
  - A assinatura de hoje passa a cobrir tudo o que se instala (achado da seção 2b).
  - O custo é o Kaique baixar o pacote inteiro, **826 MB, a cada versão**. Pela conta (não medido): uns 2 min a
    50 Mbps, 5,5 min a 20 Mbps, 11 min a 10 Mbps. Não sei a velocidade da internet dele.
- **Recomendação:** **sem diferença**, se a internet do Kaique aguentar 826 MB por versão. Fica mais rápido dos dois
  lados e fecha o buraco da assinatura, sem mudar nenhuma linha do programa. Se a internet dele for fraca, manter o
  BestSpeed e assinar também a diferença (saída (b) da seção 2b, mudança no programa, depois da entrega). É a
  pergunta 3.

### 3.4 Não refazer a pasta do programa inteira quando só o código mudou

- **Medido (M5):** `empacotar.construir_pasta` levou **10 min 16 s** no D:. O PyInstaller leva 4 min 32 s. O resto,
  uns 5,7 min, é apagar a pasta velha, copiar de novo o motor do Kraken (34 mil arquivos) e o Tesseract, e
  conferir tudo.
- **Saídas:**
  (a) montar a pasta também no C:. A cópia do motor fica perto dos 2 min da M1, e o pré-processo do Velopack cai de
  2,5–8,5 min para 0,6 min (M2b). O PyInstaller lê o `.venv` no D:, e isso não muda. Ganho estimado: uns 4 a 10 min
  somando as duas partes **[não medido junto]**. Custa mais 2 GB no C: durante o publicar.
  (b) não apagar e não copiar de novo o motor quando ele é o mesmo, conferido pela regra que já existe
  (`conferir_pecas_no_pacote`, que compara quantidade e bytes).
- **Limpa ou remendo:** a (a) é limpa e sai junto com a 3.1. A (b) é uma regra nova de "reaproveitar", e precisa de
  cuidado para nunca publicar um motor velho. Não recomendo agora.
- O Velopack copia a pasta inteira de qualquer jeito (seção 2). Por isso, reaproveitar a pasta só ajuda no passo do
  PyInstaller, não no do Velopack.

### 3.5 Deixar o motor do Kraken fora do pacote que se atualiza, instalado uma vez só

- **Como o Velopack funciona (lido na fonte):**
  - Ele cuida só da pasta `current` do programa instalado. Ao atualizar, monta a versão nova inteira e troca a pasta
    toda. O que não estiver no pacote **some** da `current`.
  - O .msi só instala dentro dessa pasta (modelo `Msi/Templates/MsiTemplate.hbs`).
  - O Velopack não tem um jeito próprio de "peça instalada uma vez e nunca trocada".
- **Então o motor teria de morar fora da pasta do programa** (por exemplo em `%ProgramData%`), instalado por outro
  caminho: um segundo instalador, ou o ajudante da primeira abertura (D-733) tirando-o de um arquivo dentro do pacote.
- **Ganho:** o pacote cai de 35.103 para uns 600 arquivos e de 1,9 para 0,8 GB. É a única saída que encurta também
  a troca de ~7,5 min no PC do Kaique **[não medido]**.
- **O que muda (muito):**
  - o lugar onde o programa procura o motor (`core/ocr_kraken.lugares_do_motor`, a regra única);
  - o teste rápido depois de atualizar (`atualizacao.teste_rapido`, que procura `motor-kraken` ao lado do .exe);
  - a instalação (D-727, tudo dentro do instalador);
  - a assinatura (o motor, fora do pacote, precisaria da sua própria);
  - o desinstalar (D-731);
  - e trocar o motor um dia, que hoje já tem aviso de "outra versão" (`_AVISO_VERSAO`).
- **Limpa ou remendo:** pode ser limpa, mas é mudança de estrutura e de instalação. Pela D-765 e pelo §11.12 ("se
  juntar os caminhos mexer em mais de uma ferramenta... o agente escreve o plano antes e espera o sim"), não é para
  agora. **Só vale estudar se, depois de 3.1 a 3.3, ainda estiver lento.**

### 3.6 Velopack mais novo

- **Lido:** a última versão estável é a **1.2.161**, a que usamos (NuGet `vpk` e PyPI `velopack`, consultados em
  18/11/2026). Existe uma prévia, `1.3.39-g8d2844f` (17/10/2026). No ramo de desenvolvimento há 107 mudanças desde
  a 1.2.161, e nenhuma acelera o empacotar.
- **O que ela traz e importa para nós:**
  - "Fix MSI uninstall cleanup and stop wiping user data on MSI upgrades" (`b40a2781`, `f31022e6`): mexe justamente
    na limpeza do desinstalador provada em 17/11. O `empacotar.py` já avisa: "SUBIR DE VERSAO EXIGE REPETIR A PROVA".
  - "Restore the previous version when a Windows update cannot replace current" (`afa30e56`).
  - "Fix zstd delta creation for non-ASCII paths on Windows" (`8d2844f3`): nomes com acento, como o do nosso
    `Editor de Impressão_ExecutionStub.exe`. **Dedução:** o Windows em português usa uma tabela de letras que tem o
    "ã", então neste PC o defeito não deve aparecer. Nas medidas, esse arquivo nunca mudou, então isso não foi
    provado nem desmentido.
- **Recomendação:** não trocar agora. Trocar biblioteca precisa perguntar (CLAUDE.md §6), ela não acelera nada, e
  obrigaria a refazer a prova do desinstalar.

## 4. Recomendação

**A combinação mais simples:**
- 3.1: o trabalho do Velopack no C:;
- 3.2: sem .msi e sem portátil nas versões de atualização, e o .msi só quando o Samuel pedir;
- 3.3: publicar sem diferença, se a internet do Kaique aguentar.

As três moram no script de publicar: duas na regra única do comando (`empacotar.comando_do_vpk`) e uma na função que
roda o vpk. Nenhuma linha do programa do Kaique muda.

**No PC do Samuel (publicar), somado das medidas por partes:**

| Passo | Hoje (D:, etapa 5) | 3.1 + 3.2, com diferença | 3.1 + 3.2 + sem diferença |
|---|---|---|---|
| Montar a pasta do programa (D:) | ~10 min | 10 min 16 s (M5) | 10 min 16 s (M5) |
| Baixar a versão anterior | 0,3 a 0,7 min | 0,3 a 0,7 min | não precisa |
| Pacote (e o resto do Velopack) | 50 a 72 min | 8 min 24 s a 15 min 21 s (M2a, M5b) | 8 min 24 s a 15 min 21 s |
| Diferença | (dentro do de cima) | 3 min 37 s a 3 min 58 s (M3, M5b) | — |
| Conferir e assinar | (ver seção 1) | ~2 s | ~2 s |
| Copiar para o servidor | 3,6 min (3,2 GB) | ~2 min (1,7 GB) **[conta pela velocidade medida]** | ~2 min |
| **Total** | **70 a 93 min** | **24 a 32 min** | **21 a 28 min** |

- A diferença entre 8,4 e 15,4 min no pacote é o pré-processo lendo do D: (2,5 min numa pasta antiga, 8,5 min numa
  recém-montada). Com a pasta do programa montada também no C: (3.4a), o pacote fica em ~7,6 min (M2b), e o total
  deve cair para uns **17 a 22 min** **[não medido junto]**.
- No GitHub de verdade, soma-se o tempo de subir pela internet, uns 1,7 GB por versão (não medido), e, com diferença,
  o de baixar os 826 MB da versão anterior.

**No PC do Kaique (atualizar), medido na etapa 5 no PC do Samuel:**

| | Com diferença (hoje) | Sem diferença |
|---|---|---|
| Baixa | ~20 MB | 826 MB |
| Remontar e trocar | ~22 a 23 min | ~7,5 min |
| A assinatura confere o que se instala? | não (seção 2b) | sim |

**O que fica de fora:** tirar o motor do Kraken do pacote (3.5), reaproveitar a pasta do programa (3.4b) e trocar o
Velopack (3.6).

**Quando o .msi é feito:** na primeira entrega ao Kaique (etapa 6) e sempre que o Samuel pedir. Por exemplo, antes
de instalar num computador novo, ou se o Velopack um dia mudar.

## 5. Perguntas para o Samuel

### Pergunta 1. Montar a versão no disco de dentro do seu PC

**Do que se trata.** É o passo de publicar uma versão nova para o Kaique. Ele roda no seu PC quando a gente manda uma
atualização, e o Kaique não vê nada disso. Hoje esse passo leva de 70 a 93 minutos por versão (medido na etapa 5,
versões 1.1.1 a 1.1.5, contando a montagem da pasta do programa).

**O que acontece hoje.** Todo o trabalho de montar a versão acontece no seu HD externo (o D:, ligado por USB). A
ferramenta copia a pasta do programa (35 mil arquivos) quatro vezes, e um HD é lento para muitos arquivos pequenos.
O disco de dentro do PC (o C:) é muito mais rápido. Medido hoje: a mesma parte que leva 20 minutos e meio no D:
levou 3 minutos e meio no C:.

**Sua dúvida:** "fazer tudo de novo sempre, eu acho que está errado né?" → Em parte, sim. A ferramenta refaz tudo de
propósito, é o jeito dela. Mas fazer isso no HD externo é o que deixa tão lento.

**O que você escolhe:**
- **Sim (sugestão):** o trabalho é feito no C:, e o rascunho é apagado no fim. Enquanto publica, ocupa de 6 a 10 GB
  do C:. O Kaique recebe exatamente a mesma atualização (conferido: o pacote sai igual, byte por byte no tamanho).
  Nada do que já funciona muda. Junto com a pergunta 2, publicar fica em uns 24 a 32 minutos.
- **Não:** continua no D:.
- **Só comentário.**

### Pergunta 2. O instalador só quando você pedir

**Do que se trata.** Quando a gente publica uma versão, saem três coisas além da atualização: o instalador (o .msi,
que o Kaique usa só na primeira vez), outro instalador menor (Setup.exe) e uma versão portátil em zip. Nenhuma delas
é usada para atualizar.

**O que acontece hoje.** As três são refeitas a cada versão. O .msi sozinho leva de 33 a 43 minutos no HD (medido),
correndo junto com a parte da atualização e atrasando ela.

**Sua dúvida:** "as atualizações deveriam ser rapidas" → Sim. O que demora no seu PC é refazer, a cada vez, coisas
que só servem para instalar do zero. (O lado do Kaique é a pergunta 3.)

**O que você escolhe:**
- **Sim (sugestão):** a versão de atualização sai sem o .msi e sem o zip portátil. O Setup.exe continua, porque a
  ferramenta não deixa tirar os dois, e leva 2 segundos para fazer. O .msi é feito na primeira entrega ao Kaique e
  sempre que você pedir. Para o Kaique, a atualização é igual. Se um dia ele instalar num computador novo, usa o
  último .msi feito, e o programa se atualiza sozinho na primeira abertura. A versão portátil do programa (a pasta)
  continua existindo.
- **Não:** tudo continua sendo refeito a cada versão.
- **Só comentário.**

### Pergunta 3. O Kaique baixa só o que mudou, ou a versão inteira?

**Do que se trata.** É a atualização que chega sozinha no notebook do Kaique quando ele abre o programa. O
programa baixa a versão nova e, com o programa fechado, troca uma pela outra.

**O que acontece hoje.** O Kaique baixa só a diferença, uns 20 MB. Mas, antes de trocar, o computador dele remonta
a versão inteira (840 MB) a partir dessa diferença. No teste de hoje no seu PC, isso levou **22 a 23 minutos** por
atualização. Quando veio a versão inteira, levou **7,5 minutos** (medido nas versões 1.1.1 a 1.1.3 da etapa 5).
E há um defeito de segurança, achado lendo o código da ferramenta (ainda não provado em teste): pelo caminho da
diferença, a assinatura do seu PC não confere o que é instalado, só a versão inteira.

**Sua dúvida:** "as atualizações deveriam ser rapidas" → No PC do Kaique, a atualização "pequena" é a mais lenta.
Quando você escolheu o Velopack (16/11), a explicação foi "baixa só o que mudou, então a atualização é rápida".
Com o nosso programa, que tem 35 mil arquivos, baixar é rápido, mas remontar demora.

**O que você escolhe:**
- **A versão inteira (sugestão, se a internet do Kaique aguentar):** ele baixa 826 MB por versão, o que leva uns
  2 min a 50 Mbps e uns 11 min a 10 Mbps (conta, não medida; não sei a internet dele). A atualização fica em
  ~7,5 min mais esse tempo. A assinatura passa a conferir tudo o que é instalado. Publicar fica uns 4 min mais rápido
  no seu PC (21 a 28 min no total). Nada muda no programa dele, só no jeito de publicar.
- **Só o que mudou, assinando também a diferença:** ele continua baixando uns 20 MB, e a atualização continua com
  ~22 min. Para fechar o defeito de segurança, o programa passa a conferir a assinatura da diferença também. Isso
  muda o programa e, pela sua regra de 17/11, fica para depois da entrega ao Kaique.
- **Deixar como está:** 20 MB, ~22 min, e o defeito de segurança continua aberto. Não recomendo.
- **Só comentário.** (Se puder, diga a velocidade da internet do Kaique.)

### Pergunta 4 (para depois, só se ainda ficar lento). Deixar o motor do Kraken fora da atualização

**Do que se trata.** O motor do Kraken é a parte do programa que acha as linhas de texto. Ele tem 1 GB e 98% dos
arquivos do programa, e nunca muda. Mesmo assim, ele entra de novo em cada versão.

**O que acontece hoje.** Ele vai dentro de cada versão. No seu PC, pesa na hora de montar a versão. No do Kaique,
pesa na troca: a maior parte dos ~7,5 minutos é abrir e trocar os 35 mil arquivos, e quase todos são do motor.

**O que você escolhe:**
- **Não agora (sugestão):** com as mudanças acima, publicar já fica em uns 21 a 32 minutos. Tirar o motor muda a
  instalação e o jeito de atualizar, e só seria estudado se ainda ficar lento.
- **Sim, estudar:** um agente escreve o plano (como o motor é instalado uma vez, conferido e desinstalado), e você
  decide antes de qualquer mudança.
- **Só comentário.**

## 6. Tabela das coisas de fora

| O que é | Licença | Roda aqui? | No notebook do Kaique? |
|---|---|---|---|
| Velopack 1.2.161 (o `vpk`, que monta e publica) | MIT | sim (medido hoje, .NET 8) | não precisa (só no PC do Samuel) |
| Velopack 1.2.161 (a parte que atualiza, dentro do programa) | MIT | sim (etapa 5) | sim (já vai no programa) |
| Velopack 1.3.39 (prévia) | MIT | não testado | não testado |
| Zstandard 1.5.5 (o `zstd.exe` dentro do vpk, faz o remendo da diferença) | BSD-3 ou GPL-2.0 (dupla) | sim | sim (dentro do Update.exe) |
| WiX 7 (cópia modificada pelo Velopack, dentro do vpk, monta o .msi) | MS-RL | sim | não precisa |
| Documentação do Velopack (velopack.docs) | MIT | — | — |

## 7. O que ficou em aberto

- **A prova do achado de segurança:** uma diferença adulterada com a assinatura certa do pacote inteiro, num
  servidor de mentira. Pela leitura do código, ela seria aceita.
- A troca no notebook do Kaique (i5-1235U) não foi medida; os tempos são do PC do Samuel.
- A velocidade da internet do Kaique e a do envio ao GitHub. Ela pesa na pergunta 3 e no envio dos 1,7 GB.
- O .msi e o portátil feitos no C:, e o publicar inteiro numa rodada só no C:, não foram medidos: o pico passaria do
  limite de 8 GB no C: combinado para este estudo. Os totais da seção 4 são a soma das partes medidas.
- **O C: perdeu uns 14 GB por outra coisa durante as medidas:** 26 GB livres às 12:06, 12,4 GB às 13:12 e 9,9 GB às
  13:32. A pasta das medidas (`C:\pr-medida`) tinha no máximo ~6 GB e só 2,5 GB no fim. Não sei de onde veio o resto.

## 8. As medidas (18/11/2026, 12:06 a 13:32, com a etapa 5 terminada)

Script `saida_teste/publicar-rapido/medir/medir.ps1`; registro `medir/medidas.log`; pico de espaço em
`medir/vigia-*.txt`. Todas com o vpk 1.2.161, sem assinatura de Windows. A etapa 5 só foi lida.

| Medida | O que fez | Resultado |
|---|---|---|
| M1 | copiar a pasta do programa (35.100 arquivos, 2,0 GB) do D: para o C: | 2 min 07 s |
| M2a | `vpk pack` da pasta do D:, TEMP e saída no C:, `--noPortable`, sem `--msi`, `--delta None` | 8 min 24 s (pré 2:31, pacote 5:47, Setup 0:02); pico 5,3 GB no C:; conferir+soma 1,5 s |
| M2b | o mesmo, com a pasta também no C: | 7 min 39 s (pré 0:36, pacote 6:58); pico 5,6 GB |
| (tentativa) | `--noInst` com `--noPortable` | recusado pelo vpk 1.2.161 |
| M3 | `vpk delta generate` no C:, 1.1.0 → 1.1.1 | BestSpeed 3 min 37 s, 18,6 MB; BestSize 3 min 33 s, 18,6 MB; pico ~4 GB |
| M4 | a mesma diferença no D:, sozinha | 20 min 33 s (13:28 comparando, 7:04 apagando); conferir+soma 21 s |
| M5 | `empacotar.construir_pasta` na cópia do estudo (D:) | 10 min 16 s (PyInstaller 4:32) |
| M5b | `vpk pack` dessa pasta nova (TEMP no C:) e a diferença real contra a 1.1.0 | pacote 15 min 21 s (pré 8:31); diferença 3 min 58 s, 21,1 MB |

## 9. Fontes consultadas (18/11/2026)

- Código do Velopack: https://github.com/velopack/velopack (etiqueta `1.2.161`; ramo `develop` em `30965450`)
- Documentação: https://github.com/velopack/velopack.docs (`docs/packaging/deltas.mdx`, `overview.mdx`,
  `reference/cli/content/vpk-windows.mdx`; commit `788ad95`)
- Versões publicadas: https://api.nuget.org/v3-flatcontainer/vpk/index.json e https://pypi.org/pypi/velopack/json
- `vpk pack -H` no PC do Samuel (opções escondidas)
- Registros da etapa 5 (só lidos): `saida_teste/etapa5/registros/publicar-1.1.0.log`, `fase1-resto-limpo.log`; os
  scripts `saida_teste/etapa5/pilotos/publicar_etapa5.py` e `fase1_resto.ps1`;
  `C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log`; o ONDE-PAREI da etapa 5
- Código do Velopack do lado do Kaique: `src/lib-rust/src/manager.rs` (`create_delta_update_strategy`,
  `download_updates`, `download_and_apply_delta_updates`, `verify_package_checksum`), `src/bins/src/commands/patch.rs`
  e `src/bins/src/commands/apply_windows_impl.rs`
- Nosso código (só lido): `publicar_versao_kaique.py`, `empacotar.py`, `atualizacao.py`, `assinatura.py`,
  `core/ocr_kraken.py`, `tests/test_decisoes_atualizacao.py`

## 10. O que ficou no disco

Ver o `ONDE-PAREI.md` (seção "Disco"), atualizado no fim da tarefa.
