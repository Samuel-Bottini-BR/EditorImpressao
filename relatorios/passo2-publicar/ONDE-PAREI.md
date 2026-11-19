# Passo 2 do plano da parte do Windows: publicar, o motor do Kraken à parte e o servidor das versões de prova (19/11/2026)

Implementador. Ramo `passo2-publicar-2026-11-19`, worktree `.claude/worktrees/passo2`, saiu de `03c91599` (a versão de
teste com o passo 1 e o porteiro ligado). Este ONDE-PAREI é também o formulário da entrega (D-792).

## Pedido

- Papel: implementador
- Commit de partida: 03c91599
- Ramo: passo2-publicar-2026-11-19

## Arquivos que vou mexer

- `publicar_versao_kaique.py`
- `empacotar.py`
- `montar_motor_kraken.py`
- `core/ocr_kraken.py`
- `versao.py`
- `core/windows.py`
- `tests/test_windows_peca.py`
- `servidor_das_versoes.py` (novo)
- `tests/test_empacotar.py`
- `tests/test_publicar_*.py` (novo)
- `relatorios/passo2-publicar/`

## Onde parei

- 19/11: leitura feita (pacote, CLAUDE.md, memória e catálogo dos erros F4, F5, F9, plano-v3 passo 2 e peças 8, 9 e
  10b, plano v1 peça 8, estudo do Kraken, estudo de publicar rápido, o código de hoje, o código do vpk 1.2.161, o do
  Velopack do lado do programa, o do `gh`). Seções de antes de escrever preenchidas abaixo. Nada rodado no Windows além
  de ler; `git -C D:\programas\EditorImpressao rev-parse --is-shallow-repository` = false.

## Decisões que esta tarefa precisa cumprir

- D-767 "não faça mais nada escodindo ou de mentira" · "não quero fazer consertos quero que funcione". Aqui: o publicar
  de verdade (montar no C:, o vpk, o rascunho no GitHub) só conta na prova à vista; os testes automáticos provam a
  lógica com uma pasta de verdade como destino e com um `gh` de mentira só para a lógica em volta do GitHub (escrito
  assim nos testes).
- D-768 "mas dai vai ter que baixar o motor do kraken toda vez e reinstalar ele de novo?" · "vou escolher a 16, vamos
  para a proxima". Aqui: a atualização sai sem o motor; o motor tem publicação própria.
- D-773 "A". Aqui: o servidor das versões de prova (janela pequena e visível; fechar é a internet caindo) e o rascunho
  no GitHub, liberado só na prova e apagado no fim.
- D-775 "o agente vai tentar quebrar antes de fazer o teste real na tela né?" · "ok". Aqui: entrego à gerente sem
  rótulo; a prova à vista vem depois de quem tenta quebrar.
- D-776 "Sim, no C só tem que cuidar para não encher o disco C inteiro". Aqui: o rascunho no C:, a conta do espaço
  antes (reserva de 20 GB), a vigia durante e o rascunho apagado no fim, também com erro.
- D-777 "mas dai vai fazer quais versões?" · "ok, fica assim". Aqui: a atualização sem .msi e sem zip portátil; o .msi
  só quando pedido.
- D-785 "ok, mais ainda existem mais casos na opção A". Aqui: publicar é da lista "sempre à vista" (item 8): não monto
  nada pesado nem publico nada; o servidor é janela à vista.
- D-786 "a". Aqui: o passo mexe em `core/ocr_kraken.py`, que o caminho do livro não usa; a gerente decide o filtro de
  velocidade.
- D-788 "1" (a primeira opção). Aqui: o motor numa pasta por versão; o instalador leva o motor como um arquivo só em
  `instalar\`.
- D-789 "mas iria demorar mais toda vez que eu fosse fazer a compilação né?" · "A". Aqui: sem o pacote de diferença
  (`--delta None`), sem baixar a versão anterior.
- D-790 "A". Aqui: antes de liberar uma versão, o publicar confere que o motor que ela pede está publicado e o lê de
  volta (a parte do Kaique é do passo 3).
- D-791 "não sei do que você está falando" · "b". Aqui: o porteiro barra desde o primeiro dia; este passo tira o item
  K01 de `empacotar.assinatura_do_arquivo` da lista no mesmo commit do conserto.
- D-795 "porque fazer isso?" · "porque ter um instalador pequeno então?" · "não tem nenhuma documentação dizendo para o
  que isso serve?" · "ok". Aqui: o Setup.exe é apagado no fim, também com erro; nunca vai ao rascunho do GitHub nem à
  pasta do servidor; a conferência do fim lê a pasta de saída e o destino.
- D-796 "não entendi" · "1, mas tem que ser explissito o pedido né". Aqui: sou implementador; não mexo em `ui/`.
- D-797 "Só precisa de dois lugares né?" · "ok". Aqui: trabalho no meu ramo; quem junta é a gerente.
- D-798 "fechou". Aqui: não escrevo o rótulo de pronto.
- D-724 "gratis, mas o que é essa assinatura e é segura?". Aqui: o motor é assinado com a mesma chave e conferido pela
  mesma peça (`assinatura.py` não muda), com outro nome de pacote.
- D-727 "pode, se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador né". Aqui: o motor vai
  dentro do instalador, como um arquivo só.
- D-807 "ok" (à pergunta "rodar tudo no seu PC só no fim. Fica assim?"). Aqui: no PC, só os arquivos de teste que
  mexi, um por vez; o conjunto inteiro no GitHub.
- D-714 "1 - vamos seguir sua sugestão" · "2- ok" · "e sim o programa pega sozinho [...]". Aqui: publicar continua só
  quando alguém roda o comando.
- D-763 "ok, pode fazer". Aqui: o nome do pacote do motor é outro (`EditorImpressaoMotorKraken`) e não é o nome da pasta
  dos projetos.

## O que já está escolhido e testado aqui

- `tests/test_empacotar.py`: o motor do jeito novo passa e o velho, com atalhos ou de outro protocolo, é recusado
  (`conferir_motor_kraken`, com um motor de mentira SEM `motor.json`: por isso essa função não pode passar a exigir a
  ficha); `achar_motor_kraken` pula o velho (troca `empacotar.LUGARES_DO_MOTOR`: o nome não pode mudar); faltando peça,
  para antes do PyInstaller; o Visual C++ oficial confere; `assinatura_do_arquivo` roda de verdade num arquivo sem
  assinatura e o resultado não confere. Os testes do Inno (o instalador de antes) continuam.
- `tests/test_decisoes_atualizacao.py`: D-714 (a versão de um lugar só; `comando_do_vpk(vpk, pasta, saida, versao)`
  com quatro argumentos tem `--packVersion`); D-724 (publicar sem a chave para antes de tudo, com `publicar(versao,
  destino_pasta=..., arquivo_da_chave=...)` e `main(["--pasta", ..., "--chave", ...]) == 1`; a chave nunca dentro do
  repositório; o que o publicar assina o programa aceita, `assinar_pacote(chave, nupkg, versao, publica)`); D-727
  (`comando_do_vpk` de fábrica tem `--msi`, `--instLocation PerMachine`, `--runtime win-x64` e nada de `--framework`;
  `preparar_pasta_para_o_velopack(pasta, pecas)` põe o Visual C++ em `instalar\`; `esperados_no_pacote_do_velopack` e
  `conferir_pacote_do_velopack` com uma `PecasDosDetectores` cujo motor nem existe).
- `tests/test_decisoes_brasao.py` (o ícone no `vpk --icon`), `tests/test_nome_do_pacote.py` (o `--packId`, o
  `--packTitle`, o vpk preso na 1.2.161, `nupkg_inteiro`).
- `tests/test_ocr_kraken.py`: `lugares_do_motor()` tem pelo menos 2 lugares e `achar_pasta_do_motor()` não quebra (o
  nome não pode mudar; e o defeito antigo nº 330, dos testes do motor que pulam calados numa cópia, continua, como o
  plano manda).
- `tests/test_windows_peca.py` e as conferências do porteiro (`tests/test_conferencias_*.py`): a peça é fechada, o
  rodar genérico recusa o PowerShell, a lista de exceções só diminui.
- Livro: D-714, D-723, D-724, D-727, D-746, D-763, D-768, D-773, D-776, D-777, D-788 a D-790, D-795 (acima).

## Como fica para quem usa e no livro

- **O Kaique:** nada muda na tela nem no livro (nenhum arquivo de `ui/` nem do processamento das páginas). O que muda
  é o que ele vai baixar a partir do passo 3: a atualização sem o motor do Kraken (uns 460 MB em vez de 826 MB, conta
  do estudo) e, na primeira instalação, o .msi com o motor dentro como um arquivo só. O PDF que sai não muda.
- **O Samuel, ao publicar (na prova à vista):** roda o mesmo comando de antes. Agora: (1) antes de tudo o comando diz
  quanto espaço vai usar no C: e para, com aviso, se o C: ficaria com menos de 20 GB livres; (2) monta no C:; (3) não
  baixa mais a versão anterior nem faz a diferença; (4) sobe como rascunho, lê de volta e só então libera; (5) no fim
  apaga o rascunho do C: e o Setup.exe, também quando dá erro, e lista o que ficou na pasta de saída e no destino.
  Para o motor, um comando próprio (`--motor`), raro. O .msi só com `--com-instalador`.
- **O servidor das versões de prova:** uma janela pequena que o Samuel vê, com o endereço, as versões que ela serve e
  uma linha por pedido. Fechar a janela corta o que estiver sendo baixado (a internet caindo).

## A causa, a regra e todos os caminhos

**Por que os defeitos aconteciam (lista do plano, itens 53 a 57, e os do estudo):**
1. O vpk era rodado por dois caminhos, cada um do seu jeito (`publicar_versao_kaique._rodar` com a pasta pronta e
   `empacotar.construir_pacote_do_velopack` com `subprocess.run`), e a pasta temporária vinha de quem chamava (a etapa 5
   a desviou à mão). Causa: não havia uma função que roda o vpk.
2. O PowerShell de `empacotar.assinatura_do_arquivo` falava com o Windows fora da peça única (item K01 da lista).
3. O motor do Kraken ia dentro de toda versão (98% dos arquivos), porque a pasta portátil, a atualização e o instalador
   eram a mesma coisa.
4. No GitHub, `vpk upload github --publish` liberava a versão antes de a assinatura subir (item 53): se a assinatura
   falhasse, a versão ficava liberada sem assinatura e o programa do Kaique a recusaria para sempre.
5. O Setup.exe e o rascunho ficavam (nada apagava) e a pasta pronta podia ser de outra versão (item 54).

**As regras, cada uma num lugar só:**
- Rodar o vpk: `empacotar.rodar_vpk` (a pasta de trabalho, a pasta temporária e a vigia do espaço).
- O comando do vpk: `empacotar.comando_do_vpk` (como hoje), com `--delta None` e `--noPortable` sempre, e o `--msi`
  só quando a saída pede.
- As três saídas (pasta portátil, atualização, instalador): `empacotar.SAIDAS`; tudo o que muda entre elas (motor
  solto, `motor-exigido.json`, o arquivo do motor em `instalar\`, o .msi, o que o pacote tem de ter e não pode ter) lê
  dali.
- A conta do espaço e a reserva: `empacotar.espaco_que_vai_usar` e `empacotar.conferir_espaco`.
- O motor "inteiro e da versão certa": `core/ocr_kraken.conferir_motor` (lê o `motor.json`); a versão do motor:
  `core/ocr_kraken.VERSAO_DO_MOTOR`; a ficha é escrita só por `montar_motor_kraken.gravar_ficha_do_motor`.
- Os nomes do motor publicado (pacote, etiqueta, arquivo): `versao.py`.
- Ler a assinatura digital de um arquivo pelo Windows: `core/windows.ler_assinatura_digital` (função própria na peça,
  o PowerShell por dentro dela).
- Publicar num destino (rascunho, enviar, ler de volta, liberar, apagar): `publicar_versao_kaique.Destino`, com dois
  jeitos (uma pasta, que o servidor das versões serve; o GitHub, pelo `gh`), e o fluxo numa função só
  (`publicar_arquivos`), usada pela versão do programa e pelo motor.
- O que vai a um destino: `publicar_versao_kaique.arquivos_da_versao` (nunca o Setup.exe).

**Todos os caminhos (achados com busca no código: `vpk`, `comando_do_vpk`, `construir_pacote_do_velopack`,
`assinatura_do_arquivo`, `motor-kraken`, `LUGARES_DO_MOTOR`, `lugares_do_motor`, `conferir_motor_kraken`, `upload`):**
- `publicar_versao_kaique.publicar` (com e sem `--pasta-pronta`) → hoje roda o vpk pelo `_rodar` dele: passa a
  `rodar_vpk`.
- `empacotar.construir_pacote_do_velopack` → hoje `subprocess.run`: passa a `rodar_vpk`.
- `vpk download` e `vpk upload local/github` em `publicar` → saem (sem diferença não há o que baixar; o envio passa a
  ser `Destino`).
- `empacotar.preparar_vc_redist` → `assinatura_do_arquivo` → passa a `windows.ler_assinatura_digital`.
- `empacotar.construir_pasta` (a pasta portátil, o `--modo pasta`, o `--modo instalador` e o `--modo entrega` do Inno, e a
  atualização) → o motor solto só quando `SAIDAS[...]` diz.
- `empacotar.conferir_pecas_no_pacote` → o motor copiado conferido por `ocr_kraken.conferir_motor`.
- `montar_motor_kraken.montar` e `--so-servidor` → gravam a ficha.
- O programa (`core/ocr_kraken.achar_pasta_do_motor`, o teste rápido, o `--conferir-ocr`, o ajudante): **não mudam neste
  passo** (passo 3 do plano). `lugares_do_motor` continua igual.
- O servidor das versões lê a mesma pasta que `Destino` (pasta) grava, pelo mesmo desenho (`versao.py` e as constantes
  do publicar), sem copiar regra.

## O que pode falhar e o que o programa faz

| O que pode dar errado | O que o publicar faz |
|---|---|
| Sem a chave, ou chave que não é a do programa | para antes de tudo (como hoje); nada é criado |
| A versão já foi publicada (ou sobrou um rascunho dela no destino) | para antes de montar, dizendo qual e como apagar o rascunho |
| O motor que a versão pede não está publicado, ou a assinatura dele não confere | para antes de montar: "publique o motor primeiro (`--motor`)" |
| Pouco espaço no C: (sobraria menos de 20 GB) | para antes de montar, dizendo quanto precisa e quanto há; nada é criado no C: |
| O C: enche durante (outra coisa usando o disco) | a vigia vê o espaço cair abaixo da reserva, fecha o vpk que este comando abriu (só ele), apaga o rascunho e diz "parei: o C: ficou com X GB" |
| O vpk falha ou não está instalado | para com o aviso; o rascunho é apagado |
| O pacote sai sem uma peça, ou com o motor dentro na atualização | para; o rascunho é apagado; nada vai ao destino |
| A pasta pronta é de outra versão, não tem a ficha, ou não tem o Visual C++ | para antes do vpk |
| Sem internet, ou o `gh` sem conta | para; se o rascunho do destino já tinha sido criado, é apagado e a apagada é conferida; se não der para apagar, a frase diz exatamente o que ficou e o comando de apagar |
| A leitura de volta não bate (o arquivo no destino tem outra soma, ou a assinatura não confere) | não libera; apaga o rascunho do destino e confere |
| O Setup.exe | é apagado logo depois de cada vpk e o rascunho inteiro some no fim (também com erro); a conferência do fim lê a pasta de saída e o destino e diz se ele está lá |
| Não consegue apagar o rascunho do C: (arquivo preso pelo antivírus) | tenta de novo por alguns segundos; se ficar, diz o caminho e o tamanho do que ficou (nunca "apagado" sem conferir) |
| Desligar o PC no meio | o rascunho fica no C: e o rascunho do destino fica sem liberar (nunca liberado pela metade); na próxima vez o comando acha o rascunho velho do destino e para dizendo como apagar; o rascunho velho do C: é apagado no começo da próxima vez (só as pastas com o nome do publicar) |
| Ctrl+C no meio | o mesmo caminho do erro: o rascunho é apagado e o do destino também |
| Arquivo preso por outro programa ao enviar | o envio falha → mesmo caminho da falha de internet |
| Sem licença de administrador | não precisa: nada do publicar pede licença (0 perguntas do Windows) |
| O servidor das versões: porta ocupada | a janela diz que a porta está ocupada e não serve nada |
| O servidor: fechar no meio de um envio | a janela corta a conexão de quem está baixando; o programa do outro lado recebe o arquivo incompleto (o Velopack confere a soma e recusa) |
| O servidor: pedido de arquivo fora da pasta ("..", caminho inteiro) | recusado (404), com a linha na janela |

## O que li da peça de fora e onde

**Lido** (código do Velopack na etiqueta `1.2.161`, commit `92d6a1c9`, cópia só para ler em
`D:\programas\EditorImpressao\saida_teste\publicar-rapido\fonte-velopack\repo`):
- `src/vpk/Velopack.Packaging/PackageBuilder.cs`, linhas 60-190: o vpk pack lê a versão anterior da pasta de saída só
  para a diferença (`GetPreviousFullRelease`; com `--delta None` não faz a diferença); se a pasta de saída já tem versão
  igual ou maior, **pergunta** ("Do you want to continue...?", `PromptYesNo`): por isso a pasta de saída é sempre nova;
  o portátil só sai sem `--noPortable`; o Setup.exe sai sempre que não houver `--noInst`; no fim move tudo para a pasta
  de saída e grava `assets.win.json` (`assetCache.Write()`) e `releases.win.json` e `RELEASES`
  (`UpdateReleaseFilesAsync`).
- `PackOptionsValidator.cs`: "Cannot use 'noPortable' and 'noInst' options together" (por isso o Setup.exe sempre sai,
  D-795).
- `src/vpk/Velopack.Vpk/Commands/Packaging/PackCommand.cs`, 88-117: `--delta` (padrão `BestSpeed`), `--noPortable` e
  `--noInst` (escondidos); `WindowsPackCommand.cs` 101: `--msi`.
- `WindowsPackCommandRunner.cs`, 200-252: o Setup.exe leva o pacote inteiro dentro; o .msi copia a pasta do programa
  outra vez e a comprime (não leva o pacote).
- `src/vpk/Velopack.Core/DefaultName.cs`: os nomes `<id>-<versao>-full.nupkg`, `<id>-win-Setup.exe`, `<id>-win.msi`,
  `<id>-win-Portable.zip` (o sufixo é "-" + o canal, "win"). Conferido na pasta da etapa 5
  (`saida_teste\etapa5\servidor`): os mesmos nomes.
- `src/lib-csharp/Util/TempUtil.cs`, 20-45: a pasta temporária do vpk é `VELOPACK_TEMP`, senão `TMPDIR`/`TEMP`/`TMP`
  + `\velopack`. Por isso `rodar_vpk` dá ao vpk `VELOPACK_TEMP`, `TEMP` e `TMP` dentro do rascunho.
- `src/vpk/Velopack.Core/BuildAssets.cs` e `src/vpk/Velopack.Deployment/_GitRelease.cs`: `vpk upload github` envia
  **todos** os arquivos de `assets.win.json` (inclusive o Setup.exe) e falha se faltar um (`File.OpenRead`); com
  `--publish` libera logo depois de enviar. Por isso o publicar não usa mais o `vpk upload`: o Setup.exe chegaria ao
  rascunho do GitHub (contra a D-795) e a liberação viria antes da assinatura. `Local.cs` e `_ObjectStore.cs`: o
  `vpk upload local` também envia todos os de `assets.win.json`.
- `src/vpk/Velopack.Packaging/ReleaseEntryHelper.cs` 100-134: o `releases.win.json` da pasta de saída lista os pacotes
  da pasta (com a pasta nova, só esta versão) com a soma SHA-256 e o tamanho; é o mesmo formato que o `vpk upload` envia
  (`GetAssetFeedJson`).
- Do lado do programa (`src/lib-rust/src/sources/http.rs` e `mod.rs`): um endereço `http://` vira `HttpSource`, que pede
  `<endereço>/releases.win.json?localVersion=...&id=...&stagingId=...` e baixa `<endereço>/<FileName>`. É o que o
  servidor das versões responde. `github.rs` (estudo do Kraken §2.2): o Velopack lê só as publicações com
  `releases.win.json` (a do motor não atrapalha).

**Lido** (o `gh` 2.99.0, instalado no PC; código `cli/cli`, `pkg/cmd/release/shared/fetch.go`, lido em 19/11):
`FetchRelease` acha uma publicação liberada pela etiqueta ou um rascunho pela etiqueta pendente; quando não acha nenhuma,
erro "release not found". Os campos de `--json` incluem `isDraft` e `assets` (cada um com `name`, `size` e `digest`).
`gh release download <etiqueta> -D <pasta>` baixa os arquivos (vale para rascunho).

**Lido** (Microsoft Learn, `SignatureStatus`): os estados de `Get-AuthenticodeSignature` são Valid, UnknownError,
NotSigned, HashMismatch, NotTrusted, NotSupportedFileFormat, Incompatible; "Valid" diz só que a assinatura é válida, a
confiança no assinante é conferida à parte (o nosso `vc_redist_confere` já confere o assinante).

**Lido** (Python 3.14): `shutil.disk_usage` (espaço livre do disco de uma pasta); `subprocess.Popen.kill` (fecha só o
processo que abrimos); `zipfile` (confere a soma de cada arquivo ao abrir, "Bad CRC-32", estudo do Kraken §3);
`http.server.ThreadingHTTPServer` (a documentação avisa que não é para servidor de produção: aqui só escuta em
127.0.0.1, na prova).

**Deduzido, não lido:** que o vpk não abre programas que continuem depois de ele ser fechado à força pela vigia (o .msi
roda o WiX por dentro; se sobrar um, o rascunho não apaga e a frase diz o que ficou).

## Perguntas do Windows que o Samuel vê

- Nesta entrega: 0 (nada pede licença; o publicar não pede).
- Na prova à vista: 0 (o plano: "0 perguntas do Windows").
