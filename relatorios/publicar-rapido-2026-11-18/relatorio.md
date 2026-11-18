# Publicar uma versão para o Kaique: por que leva quase 1 hora, e como deixar rápido

Estudo do pesquisador, 18/11/2026. Nenhuma linha do programa nem dos scripts de publicar mudou.
Ramo `publicar-rapido-2026-11-18`.

> **RASCUNHO.** Os números marcados **[não medido]** são estimativas. Eles serão trocados pelas medidas
> M1 a M5, que esperam a etapa 5 parar (ordem da gerente, 18/11, 07:20).

## A resposta, em poucas frases

1. Publicar demora porque a ferramenta (o Velopack) copia a pasta do programa inteira **quatro vezes** e comprime
   três vezes a cada versão. Para fazer a diferença, ela ainda abre de novo a versão anterior inteira. Tudo isso
   acontece no **HD externo** (o D:, ligado por USB).
2. Num HD o que pesa é a **quantidade de arquivos**, e quase todos são do motor do Kraken: 34.521 dos 35.103 (98%).
   Esse motor nunca muda.
3. Duas mudanças simples cortam a maior parte do tempo. A primeira é montar a versão no disco de dentro do PC (o C:,
   que é rápido). A segunda é só refazer o instalador e a versão portátil quando você pedir: hoje eles são refeitos
   a cada versão e só servem para a primeira instalação.
4. Com as duas juntas, publicar deve cair de **59 a 82 min** para uns **20 a 25 min** **[não medido]**. A conta é:
   uns 10 a 15 min do Velopack mais os ~11 min de montar a pasta do programa.
5. **No PC do Kaique, a atualização "pequena" é a mais lenta.** Ele baixa só uns 20 MB, mas o computador remonta
   o pacote inteiro (840 MB) antes de trocar. Na etapa 5 isso levou **22 a 23 min** por versão, contra **7,5 min**
   quando veio o pacote inteiro (medido no registro da atualização).
6. **Achado de segurança (lido no código, não provado em teste):** pelo caminho da diferença, a assinatura do PC do
   Samuel não cobre o que é instalado. Ela cobre só o pacote inteiro.
7. Publicar **sem diferença** resolve o 5 e o 6 de uma vez, e ainda tira um passo do publicar. O custo é o Kaique
   baixar 826 MB por versão. Isso é escolha do Samuel (pergunta 3), porque ele escolheu o Velopack justamente por
   "baixar só o que mudou".

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
| Conferir e assinar (nosso script) | 5:14 | 7:09 | 5:09 | 4:22 | 5:30 | ver nota |
| Copiar para o servidor | 3:37 | 3:34 | 3:38 | 3:34 | 3:39 | 3,2 GB (completo, portátil, Setup, .msi) |
| **Total da versão** | **59** | **73** | **66** | **72** | **82** min | sem contar os ~11 min de montar a pasta |

O que se vê:

- **A diferença e o .msi rodam juntos e disputam o mesmo HD.** Na 1.1.0, com o .msi sozinho, o WiX levou 13 min.
  Nas outras, com a diferença rodando junto, levou de 25 a 28 min.
- **Uns 7 min da "diferença" são só para apagar** os arquivos que ela mesma abriu: do "Delta processed" ao
  "Complete" do registro. O código do Velopack apaga as pastas temporárias nesse ponto.
- **Fica mais lento a cada versão** (59 → 82 min). O pré-processo, que é só uma cópia, foi de 3,5 para 10 min. Isso
  combina com um HD que vai enchendo e se espalhando, mas não foi medido.
- **Conferir e assinar (4 a 7 min)** deveria levar segundos: é ler 826 MB uma vez. A suspeita é o antivírus do
  Windows abrindo o pacote recém-criado, que tem 35 mil arquivos dentro **[não medido; M2 separa]**.

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

O C: é um SSD NVMe de 512 GB (WD SN530), com 28 GB livres. O D: é um HD externo USB de 2 TB (WD easystore), com
185 GB livres. O processador é um Ryzen 7 5800H (8 núcleos, 16 linhas), com 15 GB de memória. O TEMP do publicar
estava desviado para `saida_teste\etapa5\temp`, no D:.

## 2. Por que é assim (lido no código do Velopack 1.2.161, licença MIT)

Fonte: `github.com/velopack/velopack`, etiqueta `1.2.161` (commit `92d6a1c9`, 29/09/2026), copiada em
`saida_teste/publicar-rapido/fonte-velopack/repo`. Arquivos lidos: `src/vpk/Velopack.Packaging/PackageBuilder.cs`,
`src/vpk/Velopack.Packaging.Windows/Commands/WindowsPackCommandRunner.cs`,
`src/vpk/Velopack.Packaging/Compression/DeltaPackageBuilder.cs`, `src/lib-csharp/Util/EasyZip.cs`,
`src/lib-csharp/Util/TempUtil.cs`, `src/vpk/Velopack.Packaging.Windows/Msi/`.

**Lido na fonte:**

- **Pré-processo** (`PreprocessPackDir`): copia a pasta inteira para `%TEMP%\velopack\...`, arquivo por arquivo.
- **Pacote completo** (`CreateReleasePackage`): copia **de novo** para outra pasta temporária e comprime num zip, num
  processo só e no nível "Optimal".
- **Portátil** (`CreatePortablePackage`): copia **de novo** e comprime outro zip, ao mesmo tempo que o completo.
- **Setup.exe**: copia o pacote completo (826 MB) para dentro de um .exe.
- **.msi**: copia a pasta **pela quarta vez** e o WiX comprime tudo num arquivo dentro do .msi. O .msi leva os
  arquivos do programa soltos, não o pacote.
- **Diferença** (`DeltaPackageBuilder`): descompacta **os dois pacotes inteiros** (o anterior e o novo, uns 70 mil
  arquivos). Compara cada arquivo byte a byte. Para cada arquivo igual, grava **dois arquivos vazios** de marcação
  e apaga o original. Só o arquivo que mudou passa pelo Zstandard, que é onde entra o modo (BestSpeed ou BestSize).
  No fim, comprime tudo e apaga as pastas.
- Tudo vai para `%TEMP%\velopack` (`TempUtil`). Por isso, desviar o TEMP muda o disco de todo esse trabalho.
- As opções escondidas (`vpk pack -H`): `--noInst` ("Skip generating an installer package", sem Setup.exe nem .msi),
  `--noPortable` (sem portátil) e `--delta None|BestSpeed|BestSize`. O `--msi` não vem ligado de fábrica: nós o
  ligamos (`empacotar.comando_do_vpk`).

**Dedução minha (a medir):** cada versão escreve no HD uns 18 GB em ~210 mil arquivos pequenos. São 4 cópias de
1,9 GB, 2 descompactações de 1,9 GB, os 70 mil arquivos vazios, as saídas e a cópia de 3,2 GB para o servidor. Um
HD USB grava poucas centenas de arquivos pequenos por segundo; um SSD NVMe, dezenas de milhares. Por isso a hipótese
principal é **disco**, não processador nem compressão. A M2 e a M4 separam isso: o mesmo trabalho no C: e no D:.

**Os 19,5 MB da diferença são quase só "papel" (medido, só lendo o pacote 1.1.5):** o arquivo tem 70.210 entradas.
Só 6 têm conteúdo, uns 140 KB somados (o ícone do instalador e a marcação da versão). O resto são as entradas vazias
de "não mudou", e cada uma ocupa uns 280 bytes de cabeçalho no zip. Com o código mudado de verdade, entra também o
remendo do `EditorImpressao.exe` (21,8 MB, onde mora o código). O tamanho real da diferença será medido na M5.

## 2b. O lado do Kaique: quanto ele baixa e quanto tempo a troca leva

Medido no registro da atualização da etapa 5 (`C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log`, só
lido), no PC do Samuel. O programa estava instalado no C: (SSD) e as versões vinham de uma pasta no D:.

| Versão | Caminho | "Baixando" (do registro) | Trocar e conferir | Total |
|---|---|---|---|---|
| 1.1.0 → 1.1.1 | pacote inteiro (826 MB) | 17 s (09:07:22 a 09:07:39) | 7 min 15 s (09:27:17 a 09:34:32) | ~7,5 min |
| 1.1.1 → 1.1.2 | diferença (19,5 MB) | 14 min 56 s (09:36:40 a 09:51:36) | 7 min 53 s (a 09:59:29) | ~23 min |
| 1.1.2 → 1.1.3 | diferença (19,5 MB) | 14 min 21 s (10:00:18 a 10:14:39) | 7 min 49 s (o teste rápido recusou, como devia) | ~22 min |

**Por que (lido no código do Velopack, `src/lib-rust/src/manager.rs` e `src/bins/src/commands/patch.rs`):**

- A **primeira** atualização depois do .msi veio pelo pacote inteiro. O .msi não deixa o pacote da versão instalada
  na pasta `packages`, e sem ele a diferença não tem de onde partir (`create_delta_update_strategy`: "no local/base
  package available"). Isso confirma o que era só dedução no rascunho.
- **Pela diferença**, o "baixando" inclui remontar o pacote inteiro. O Velopack descompacta o pacote anterior inteiro
  (35 mil arquivos), aplica a diferença e **comprime tudo de novo** num pacote de 840 MB (`patch.rs`, `delta`; o
  remontado da 1.1.3 ficou com 839.424.186 bytes, o publicado tem 826.530.083). Baixar os 19,5 MB é o de menos.
- **A troca** (`apply_windows_impl.rs`) descompacta o pacote inteiro mais uma vez numa pasta temporária, troca as
  pastas e apaga a velha. São de novo 35 mil arquivos, cada um lido pelo antivírus. Depois vem o nosso teste rápido.
- Então a diferença **economiza internet, mas custa uns 15 min a mais de trabalho do computador**. No notebook do
  Kaique (i5-1235U) deve ser parecido ou mais lento **[não medido]**.

**Quanto ele baixa de verdade:** pela diferença, 19,5 MB (quase só as entradas vazias de "não mudou"; com código
mudado, um pouco mais, M5). Pelo pacote inteiro, 826 MB. Na primeira atualização depois de instalar, sempre o
inteiro.

### Achado de segurança: a diferença não passa pela assinatura (lido no código, não provado em teste)

- **O que a assinatura cobre hoje** (`atualizacao._versao_assinada_do`): o nome do pacote, a versão, o nome do
  arquivo do pacote **inteiro** e a soma dele. O programa confere isso **antes de baixar** (D-724).
- **Pelo caminho da diferença**, o Velopack confere a diferença baixada contra a soma escrita no arquivo de versões
  do servidor (`releases.win.json`), que **não é assinado** (`verify_package_checksum` no `delta`). Depois ele
  monta o pacote novo e **não o compara com a soma assinada**: o `patch.rs` pula as somas ("skip shasum files"), e o
  remontado nem tem o mesmo tamanho do publicado.
- **Consequência (dedução):** quem conseguisse trocar os arquivos de uma versão no GitHub (por exemplo, com a conta
  ou o token do Samuel) poderia publicar uma diferença adulterada. A assinatura verdadeira do pacote inteiro
  continuaria lá. A D-724 diz que "versão sem a assinatura certa não é instalada", e pelo caminho da diferença isso
  não está garantido.
- **O que foi provado na etapa 5:** a 1.1.4, com assinatura de chave falsa, foi recusada. Essa prova é sobre a
  assinatura do pacote inteiro. Uma diferença adulterada com a assinatura certa nunca foi testada.
- **Saídas:**
  (a) publicar **sem diferença**: o programa sempre baixa o pacote inteiro, conferido pela soma assinada. Nada muda
  no programa (só uma opção no comando do publicar);
  (b) manter a diferença e **assinar também a diferença**: o publicar põe a soma dela na assinatura, e o programa
  confere antes de baixar. É mudança no programa (`assinatura.py`, `atualizacao.py`), e pela D-765 espera a entrega;
  (c) desligar a diferença no próprio programa (`MaximumDeltasBeforeFallback`, opção do Velopack). Também é mudança
  no programa.
- **Limpa ou remendo:** a (a) e a (b) são limpas. A (b) mora num lugar só (`_versao_assinada_do` e
  `assinatura.VersaoAssinada`). A (c) deixaria diferenças publicadas que ninguém usa.

## 3. Cada saída possível

Para cada uma: quanto economiza, o que muda para o Kaique, a segurança (a assinatura, D-724), a etapa 5, e se é
solução limpa ou remendo (CLAUDE.md §11.12).

### 3.1 Montar a versão no C: (SSD) em vez do D: (HD externo)

- **Economiza:** a maior parte dos 50 a 72 min do Velopack. Estimativa: o Velopack cai para uns 10 a 15 min
  **[não medido; M2 e M3]**.
- **Para o Kaique:** nada muda. O pacote é o mesmo, byte a byte no que importa.
- **Assinatura:** igual. Ela é feita depois, sobre o pacote pronto.
- **Etapa 5:** não é tocada. O servidor de mentira continua onde está; só a pasta de rascunho muda de lugar.
- **Custo:** precisa de uns 9 a 12 GB livres no C: **durante** o publicar, apagados no fim **[não medido; a M2 mede
  o pico]**. O C: tem 28 GB livres hoje e já ficou cheio em 05/10.
- **Limpa ou remendo:** limpa, se feita num lugar só. Hoje o rascunho mora em
  `publicar_versao_kaique.PASTA_DE_TRABALHO` (`build\publicar`, ao lado do código, no D:). O TEMP vem de quem chama:
  a etapa 5 o desviou à mão no `fase1_resto.ps1`. O vpk é chamado por **dois caminhos**:
  `publicar_versao_kaique.publicar` (com `--pasta-pronta`, por `_rodar`) e
  `empacotar.construir_pacote_do_velopack` (por `subprocess.run`). Os dois usam a mesma regra do comando
  (`empacotar.comando_do_vpk`), mas cada um roda o processo do seu jeito. O conserto limpo é **uma** função que roda
  o vpk com a pasta de trabalho e o TEMP certos, chamada pelos dois caminhos. Desviar o TEMP só num deles seria remendo.

### 3.2 Não gerar o instalador (.msi e Setup.exe) nem o portátil nas versões de atualização

- **Economiza:** no D:, a 4ª cópia mais o WiX (25 a 43 min que hoje correm junto com a diferença e a atrasam), a 3ª
  cópia e uma compressão (o portátil), e 2,4 GB a menos para enviar. No C:, uns 3 a 6 min **[não medido]**. **No
  GitHub de verdade isso pesa mais:** cada versão hoje sobe 3,2 GB pela internet (completo, portátil, Setup e .msi).
  Só com o completo e a diferença, sobem uns 850 MB.
- **Para o Kaique:** a atualização é igual. Ela usa só o pacote completo e a diferença, não o instalador (lido em
  `atualizacao.procurar_e_preparar` e no código do Velopack, `lib-rust/src/manager.rs`). Muda só uma coisa: numa
  **instalação nova** (outro computador, ou reinstalar), o instalador disponível é o da última versão que o gerou. O
  programa instalado por ele se atualiza sozinho na primeira abertura (D-732).
- **Assinatura:** igual. O que se assina é o pacote completo, que continua saindo sempre.
- **Desinstalar:** quem desinstala é o .msi da **primeira** instalação, que o Windows guarda. O que foi provado em
  17/11 (D-763/D-764, Velopack 1.2.161) continua valendo.
- **Etapa 5:** nada muda nela. Ela já tem o .msi da 1.1.0.
- **Versão portátil (D-300, "Instalador em português, com desinstalador e versão portátil"):** a versão portátil do
  nosso programa é a pasta que o `empacotar.py --modo pasta` monta, e ela continua existindo. O zip portátil do
  Velopack é outra, que a etapa 5 nem usa. Mesmo assim, tirá-la muda o que sai do publicar: vai na pergunta 2.
- **Limpa ou remendo:** limpa. A regra do comando já mora num lugar só (`empacotar.comando_do_vpk`). Basta uma
  escolha "com instalador" (ligada de fábrica, como hoje) e uma opção no publicar para desligá-la. Com a escolha
  ligada de fábrica, o teste antigo `tests/test_decisoes_atualizacao.py::test_d727_o_vpk_nao_baixa_nada_na_hora_de_instalar`
  (que cobra o `--msi`) continua valendo sem mudar. Seria preciso um teste novo para o caminho "sem instalador".

### 3.3 O modo da diferença (None, BestSpeed, BestSize)

- **Lido na fonte:** o modo só age no arquivo que mudou de verdade (o Zstandard, `Zstd.CreatePatch`). Os outros 35
  mil arquivos passam pelo mesmo caminho em qualquer modo. A documentação (`docs/packaging/deltas.mdx`) diz que o
  BestSize é "a lot slower, about on-par with the bsdiff algorithm".
- **BestSpeed (hoje):** o Kaique baixa uns 20 MB por versão **[a confirmar com código mudado: M5]**.
- **BestSize:** mais lento, e o ganho é só no remendo do .exe, poucos MB no máximo. Não compensa **[M3 mede]**.
- **None (sem diferença):** tira o passo inteiro do publicar (28 a 37 min no D:, uns 3 a 5 min no C:
  **[não medido]**). No PC do Kaique, tira os ~15 min de remontar o pacote (seção 2b): a atualização fica em ~7,5 min
  mais o tempo de baixar. A assinatura de hoje passa a cobrir tudo o que se instala (achado da seção 2b). O custo é
  o Kaique baixar o pacote inteiro, **826 MB, a cada versão**: uns 2 min a 50 Mbps, 5,5 min a 20 Mbps, 11 min a
  10 Mbps (conta, não medido). Não sei a velocidade da internet dele.
- **Recomendação (mudou depois da seção 2b):** **sem diferença**, se a internet do Kaique aguentar 826 MB por versão.
  Fica mais rápido dos dois lados e fecha o buraco da assinatura, sem mudar nenhuma linha do programa. Se a
  internet dele for fraca, manter o BestSpeed e assinar também a diferença (saída (b) da seção 2b, mudança no
  programa, depois da entrega). É a pergunta 3.

### 3.4 Não refazer a pasta do programa inteira quando só o código mudou

- **Hoje** (`empacotar.construir_pasta`): apaga o `dist\EditorImpressao` inteiro, roda o PyInstaller (uns 3,5 min
  no registro da 1.1.0) e copia de novo o motor do Kraken (34 mil arquivos) e o Tesseract. Ao todo, ~7 a 11 min.
- **Saídas:**
  (a) montar a pasta também no C: (a cópia do motor fica rápida; o PyInstaller lê o `.venv` no D:, e isso não muda);
  (b) não apagar e não copiar de novo o motor quando ele é o mesmo, conferido pela regra que já existe
  (`conferir_pecas_no_pacote`, que compara quantidade e bytes).
- **Economia:** uns 3 a 5 min **[não medido]**.
- **Limpa ou remendo:** a (a) é limpa e sai junto com a 3.1. A (b) é uma regra nova de "reaproveitar"; precisa de
  cuidado para nunca publicar um motor velho. Não recomendo agora.
- O Velopack copia a pasta inteira de qualquer jeito (seção 2). Por isso, reaproveitar a pasta só ajuda no passo do
  PyInstaller, não no do Velopack.

### 3.5 Deixar o motor do Kraken fora do pacote que se atualiza, instalado uma vez só

- **Como o Velopack funciona (lido na fonte):** ele cuida só da pasta `current` do programa instalado. Ao atualizar,
  monta a versão nova inteira e troca a pasta toda. O que não estiver no pacote **some** da `current`. O .msi só
  instala dentro dessa pasta (modelo `Msi/Templates/MsiTemplate.hbs`). O Velopack não tem um jeito próprio de
  "peça instalada uma vez e nunca trocada".
- **Então o motor teria de morar fora da pasta do programa** (por exemplo em `%ProgramData%`), instalado por outro
  caminho: um segundo instalador, ou o ajudante da primeira abertura (D-733) tirando-o de um arquivo dentro do pacote.
- **Ganho:** o pacote cai de 35.103 para uns 600 arquivos e de 1,9 para 0,8 GB. Publicar ficaria rápido até no D:
  **[não medido]**.
- **O que muda (muito):** o lugar onde o programa procura o motor (`core/ocr_kraken.lugares_do_motor`, a regra
  única); o teste rápido depois de atualizar (`atualizacao.teste_rapido`, que procura `motor-kraken` ao lado do .exe);
  a instalação (D-727, tudo dentro do instalador); a assinatura (o motor, fora do pacote, precisaria da sua própria);
  o desinstalar (D-731); e trocar o motor um dia, que hoje já tem aviso de "outra versão" (`_AVISO_VERSAO`).
- **Limpa ou remendo:** pode ser limpa, mas é mudança de estrutura e de instalação. Pela D-765 e pelo §11.12 ("se
  juntar os caminhos mexer em mais de uma ferramenta... o agente escreve o plano antes e espera o sim"), não é para
  agora. **Só vale estudar se, depois de 3.1 e 3.2, ainda estiver lento.**

### 3.6 Velopack mais novo

- **Lido:** a última versão estável é a **1.2.161**, a que usamos (NuGet `vpk` e PyPI `velopack`, consultados em
  18/11/2026). Existe uma prévia, `1.3.39-g8d2844f` (17/10/2026). No ramo de desenvolvimento há 107 mudanças desde
  a 1.2.161; nenhuma acelera o empacotar.
- **O que ela traz e importa para nós:**
  - "Fix MSI uninstall cleanup and stop wiping user data on MSI upgrades" (`b40a2781`, `f31022e6`): mexe justamente
    na limpeza do desinstalador provada em 17/11. O `empacotar.py` já avisa: "SUBIR DE VERSAO EXIGE REPETIR A PROVA".
  - "Restore the previous version when a Windows update cannot replace current" (`afa30e56`).
  - "Fix zstd delta creation for non-ASCII paths on Windows" (`8d2844f3`): nomes com acento, como o do nosso
    `Editor de Impressão_ExecutionStub.exe`. **Dedução:** o Windows em português usa uma tabela de letras que tem o
    "ã", então neste PC o defeito não deve aparecer. Nas cinco versões da etapa 5 esse arquivo nunca mudou, então
    isso não foi provado nem desmentido.
- **Recomendação:** não trocar agora. Trocar biblioteca precisa perguntar (CLAUDE.md §6), ela não acelera nada, e
  obrigaria a refazer a prova do desinstalar.

## 4. Recomendação

**A combinação mais simples:** 3.1 (montar no C:) + 3.2 (instalador e portátil só quando você pedir) + publicar sem
diferença (3.3 "None", se a internet do Kaique aguentar). As três moram no script de publicar: duas na regra única
do comando (`empacotar.comando_do_vpk`) e uma na função que roda o vpk. Nenhuma linha do programa do Kaique muda.

**No PC do Samuel (publicar):**

| | Hoje (D:) | 3.1 + 3.2 (C:) | 3.1 + 3.2 + sem diferença (C:) |
|---|---|---|---|
| Velopack | 50 a 72 min | 8 a 15 min **[não medido]** | 4 a 10 min **[não medido]** |
| Conferir, assinar, enviar | 8 a 11 min | 1 a 2 min **[não medido]** | 1 a 2 min **[não medido]** |
| Montar a pasta do programa | ~11 min | ~8 min **[não medido]** | ~8 min **[não medido]** |
| **Total** | **70 a 93 min** | **17 a 25 min** | **13 a 20 min** |

(No GitHub de verdade, soma-se o tempo de subir pela internet: hoje 3,2 GB por versão; com a 3.2, uns 850 MB; sem
diferença, 826 MB.)

**No PC do Kaique (atualizar), medido na etapa 5 no PC do Samuel:**

| | Com diferença (hoje) | Sem diferença |
|---|---|---|
| Baixa | 19,5 MB | 826 MB |
| Remontar e trocar | ~22 a 23 min | ~7,5 min |
| A assinatura cobre o que se instala? | não (seção 2b) | sim |

**O que fica de fora:** tirar o motor do Kraken do pacote (3.5; é a única saída que encurta também a troca de
~7,5 min, e só vale estudar se ainda ficar lento), reaproveitar a pasta do programa (3.4b) e trocar o Velopack (3.6).

**Quando o instalador é feito:** na primeira entrega ao Kaique (etapa 6) e sempre que você pedir. Por exemplo,
antes de instalar num computador novo, ou se o Velopack um dia mudar.

## 5. Perguntas para o Samuel

### Pergunta 1. Montar a versão no disco de dentro do seu PC

**Do que se trata.** É o passo de publicar uma versão nova para o Kaique. Ele roda no seu PC quando a gente manda uma
atualização, e o Kaique não vê nada disso. Hoje esse passo leva de 59 a 82 minutos por versão (medido na etapa 5,
versões 1.1.1 a 1.1.5).

**O que acontece hoje.** Todo o trabalho de montar a versão acontece no seu HD externo (o D:, ligado por USB). A
ferramenta copia a pasta do programa (35 mil arquivos) quatro vezes, e um HD é lento para muitos arquivos pequenos.
O disco de dentro do PC (o C:) é muito mais rápido.

**Sua dúvida:** "fazer tudo de novo sempre, eu acho que está errado né?" → Em parte, sim. A ferramenta refaz tudo de
propósito: é o jeito dela. Mas fazer isso no HD externo é o que deixa tão lento. No disco de dentro, o mesmo trabalho
deve levar uns 15 a 25 minutos **[não medido]**.

**O que você escolhe:**
- **Sim (sugestão):** a versão é montada no C: e o rascunho é apagado no fim. Enquanto publica, ocupa uns 9 a 12 GB
  do C:, que tem 28 GB livres hoje. O Kaique recebe exatamente a mesma atualização. Nada do que já funciona muda.
- **Não:** continua no D:, com os mesmos 59 a 82 minutos.
- **Só comentário.**

### Pergunta 2. O instalador só quando você pedir

**Do que se trata.** Quando a gente publica uma versão, saem três coisas além da atualização: o instalador (o .msi,
que o Kaique usa só na primeira vez), outro instalador (Setup.exe) e uma versão portátil em zip. Nenhuma delas é
usada para atualizar.

**O que acontece hoje.** As três são refeitas a cada versão. O instalador sozinho leva de 25 a 43 minutos no HD
(medido), correndo junto com a parte da atualização e atrasando ela. E, no GitHub, cada versão sobe 3,2 GB em vez de
850 MB.

**Sua dúvida:** "as atualizações deveriam ser rapidas" → Sim. O que demora no seu PC é refazer, a cada vez, coisas
que só servem para instalar do zero. (O lado do Kaique é a pergunta 3.)

**O que você escolhe:**
- **Sim (sugestão):** a versão de atualização sai sem instalador e sem o zip portátil. O instalador é feito na
  primeira entrega ao Kaique e sempre que você pedir. Para o Kaique, a atualização é igual. Se um dia ele instalar
  num computador novo, usa o último instalador feito, e o programa se atualiza sozinho na primeira abertura. A
  versão portátil do programa (a pasta) continua existindo. Economiza uns 3 a 6 minutos no C: **[não medido]** e
  uns 25 a 40 no D:.
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
- **A versão inteira (sugestão, se a internet do Kaique aguentar):** ele baixa 826 MB por versão. Isso leva uns
  2 min a 50 Mbps e uns 11 min a 10 Mbps (conta, não medido; não sei a internet dele). A atualização fica em ~7,5 min
  mais esse tempo. A assinatura passa a cobrir tudo o que é instalado. Publicar fica uns 4 a 5 min mais rápido no seu
  PC. Nada muda no programa dele, só no jeito de publicar.
- **Só o que mudou, assinando também a diferença:** ele continua baixando uns 20 MB, e a atualização continua com
  ~22 min. Para fechar o defeito de segurança, o programa passa a conferir a assinatura da diferença também. Isso
  muda o programa, e pela sua regra de 17/11 fica para depois da entrega ao Kaique.
- **Deixar como está:** 20 MB, ~22 min, e o defeito de segurança continua aberto. Não recomendo.
- **Só comentário.** (Se puder, diga a velocidade da internet do Kaique.)

### Pergunta 4 (para depois, só se ainda ficar lento). Deixar o motor do Kraken fora da atualização

**Do que se trata.** O motor do Kraken é a parte do programa que acha as linhas de texto. Ele tem 1 GB, 98% dos
arquivos do programa, e nunca muda. Mesmo assim, ele entra de novo em cada versão.

**O que acontece hoje.** Ele vai dentro de cada versão. No seu PC, pesa na hora de montar a versão. No do Kaique,
pesa na troca: a maior parte dos ~7,5 minutos é abrir e trocar os 35 mil arquivos, e quase todos são do motor.

**O que você escolhe:**
- **Não agora (sugestão):** com as mudanças acima, publicar já deve ficar em uns 15 a 20 minutos. Tirar o motor muda
  a instalação e o jeito de atualizar, e só seria estudado se ainda ficar lento.
- **Sim, estudar:** um agente escreve o plano (como o motor é instalado uma vez, conferido e desinstalado) e você
  decide antes de qualquer mudança.
- **Só comentário.**

## 6. Tabela das coisas de fora

| O que é | Licença | Roda aqui? | No notebook do Kaique? |
|---|---|---|---|
| Velopack 1.2.161 (o `vpk`, que monta e publica) | MIT | sim (já instalado, .NET 8) | não precisa (só no PC do Samuel) |
| Velopack 1.2.161 (a parte que atualiza, dentro do programa) | MIT | sim | sim (já vai no programa) |
| Velopack 1.3.39 (prévia) | MIT | sim, não testado | sim, não testado |
| Zstandard 1.5.5 (o `zstd.exe` dentro do vpk, faz o remendo da diferença) | BSD-3 ou GPL-2.0 (dupla) | sim | não precisa |
| WiX 7 (cópia modificada pelo Velopack, dentro do vpk, monta o .msi) | MS-RL | sim | não precisa |
| Documentação do Velopack (velopack.docs) | MIT | — | — |

## 7. O que ficou em aberto

- Todos os números **[não medido]**: esperam as medidas M1 a M5 (depois da etapa 5).
- Por que "conferir e assinar" leva 4 a 7 min (suspeita: o antivírus abrindo o pacote).
- O tamanho real da diferença quando o código muda (M5).
- O pico de espaço no C: durante o publicar (M2).
- Não sei a velocidade da internet do Kaique nem a do envio ao GitHub; isso pesa no "None" e no envio do pacote.
- Confirmado pelo registro da etapa 5: a **primeira** atualização depois do .msi baixa o pacote inteiro.
- O achado de segurança da seção 2b foi tirado da leitura do código. Falta uma prova: uma diferença adulterada com a
  assinatura certa do pacote inteiro, num servidor de mentira. Pela leitura, ela seria aceita.
- A troca no notebook do Kaique (i5-1235U) não foi medida; os tempos são do PC do Samuel.

## 8. Fontes consultadas (18/11/2026)

- Código do Velopack: https://github.com/velopack/velopack (etiqueta `1.2.161`; ramo `develop` em `30965450`)
- Documentação: https://github.com/velopack/velopack.docs (`docs/packaging/deltas.mdx`, `overview.mdx`,
  `reference/cli/content/vpk-windows.mdx`; commit `788ad95`)
- Versões publicadas: https://api.nuget.org/v3-flatcontainer/vpk/index.json e https://pypi.org/pypi/velopack/json
- `vpk pack -H` no PC do Samuel (opções escondidas)
- Registros da etapa 5: `saida_teste/etapa5/registros/publicar-1.1.0.log`, `fase1-resto-limpo.log`; scripts
  `saida_teste/etapa5/pilotos/publicar_etapa5.py`, `fase1_resto.ps1` (só lidos)
- Registro da atualização da etapa 5: `C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log` (só lido) e o
  ONDE-PAREI da etapa 5 (`.claude/worktrees/etapa5/relatorios/frente-kaique-2026-11-16/etapa5/ONDE-PAREI.md`)
- Código do Velopack do lado do Kaique: `src/lib-rust/src/manager.rs` (`create_delta_update_strategy`,
  `download_updates`, `download_and_apply_delta_updates`, `verify_package_checksum`), `src/bins/src/commands/patch.rs`,
  `src/bins/src/commands/apply_windows_impl.rs`
- Nosso código (só lido): `publicar_versao_kaique.py`, `empacotar.py`, `atualizacao.py`, `assinatura.py`,
  `core/ocr_kraken.py`, `tests/test_decisoes_atualizacao.py`

## 9. O que ficou no disco

- D: `saida_teste/publicar-rapido/fonte-velopack/` (código e documentação do Velopack, ~0,5 GB). Pode ser apagada no
  fim do estudo.
- C: nada até agora.
