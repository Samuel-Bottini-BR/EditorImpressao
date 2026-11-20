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
  Velopack do lado do programa, o do `gh`). Seções de antes de escrever preenchidas.
- 19/11: código e testes feitos, em commits pequenos (lista em "Commit"). Prova de reversão: 19 de 19 proteções
  acusadas pelo seu teste (`anexos/reversao-resultado.txt`); os testes novos falham no código antigo
  (`anexos/reversao-codigo-antigo.txt`). Rodada do GitHub em "Testes".
- `git -C D:\programas\EditorImpressao rev-parse --is-shallow-repository` = false antes e depois. Nenhum atalho de
  pasta (junção) foi criado: nada foi montado de verdade (o vpk e o PyInstaller ficam para a prova à vista).
- 19/11: a rodada 1 do GitHub (44642471223) achou um defeito de verdade: no Windows do GitHub o PowerShell aberto pela
  peça herdava os módulos do PowerShell 7 e não lia a assinatura digital. Consertado na peça (`fa28ab5b`), com teste de
  reversão que refaz o caso no PC (falhou antes do conserto, passa depois). Achado junto, sem consertar (não é deste
  passo): o lançar solto dá "saiu sem começar" para um script rápido (Lista de bugs, em "Ideias e bugs").
- 19/11: pedido da gerente (D-809, D-811, D-812, D-814): consertado o apagar do lançar solto (`64ed0c01`) e o
  apagar do destino com atalho (`0ef0da17`), com testes que falham sem o conserto; as três seções novas do formulário.
- 19/11 (noite): quem tentou quebrar devolveu (volta 1, `quem-quebrou/relatorio-1.md`, commit `a58f181b`): 11
  achados. A gerente pediu o conserto de todos (o 4 por decisão técnica dela, D-014). **Feita a volta 2** (`17cd8635`,
  `85781a08`): os 11 achados com destino em "O que o agente que tentou quebrar achou", cada conserto com o teste que
  falha sem ele (`anexos/reversao-volta2-resultado.txt`). **Próximo:** a gerente manda a quem tenta quebrar de novo.
- **Próximo (antes):** a gerente manda a quem tenta quebrar; depois a prova à vista (o roteiro está em "A prova de verdade").
- 20/11, **volta 3 (agente novo, D-815)**: começo pelo relatório 2 de quem tentou quebrar (`quem-quebrou/relatorio-2.md`,
  10 achados). Pedido da gerente: consertar 1 a 9 pela causa, com teste que falha sem o conserto (D-811), e anotar o 10
  para o passo 3. Leitura feita (implementador, CLAUDE.md, memória, catálogo, pacote, este formulário, os dois
  relatórios, o Livro D-809 a D-815). Andamento em "Volta 3" abaixo de "O que o agente que tentou quebrar achou".
- 20/11, volta 3 feita: os 10 achados do relatório 2 com destino em "O que o agente que tentou quebrar achou"
  (código em `411b46c7`, `d628be0e`, `1b430752`, `4817c2f4`, `05f743ca`, `e4263c0a`); cada conserto com o teste que falha sem ele
  (`anexos/reversao-volta3-codigo-antigo.txt`: os testes novos falham no código da volta 2; `anexos/reversao-volta3-resultado.txt`:
  24 de 24 proteções desligadas numa cópia, todas acusadas). `--is-shallow-repository` = false antes e depois; nenhuma
  junção criada. **Próximo:** a gerente manda a um agente novo que tenta quebrar (D-815); depois a prova à vista.

## Decisões que esta tarefa precisa cumprir

- D-767 "não faça mais nada escodindo ou de mentira" · "não quero fazer consertos quero que funcione". Aqui: o publicar
  de verdade (montar no C:, o vpk, o rascunho no GitHub) só conta na prova à vista; os testes automáticos provam a
  lógica com uma pasta de verdade como destino e com um vpk e um `gh` de mentira só para a lógica em volta (escrito
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
- D-785 "ok, mais ainda existem mais casos na opção A". Aqui: publicar é da lista "sempre à vista" (item 8): não montei
  nada pesado nem publiquei nada; o servidor é janela à vista.
- D-786 "a". Aqui: o passo mexe em `core/ocr_kraken.py`, que o caminho do livro não usa; a gerente decide o filtro de
  velocidade.
- D-788 "1" (a primeira opção). Aqui: o motor numa pasta por versão; o instalador leva o motor como um arquivo só em
  instalar\.
- D-789 "mas iria demorar mais toda vez que eu fosse fazer a compilação né?" · "A". Aqui: sem o pacote de diferença,
  sem baixar a versão anterior.
- D-790 "A". Aqui: antes de liberar uma versão, o publicar confere que o motor que ela pede está publicado e o lê de
  volta (a parte do Kaique é do passo 3).
- D-791 "não sei do que você está falando" · "b". Aqui: o porteiro barra desde o primeiro dia; este passo tira o item
  de `empacotar.assinatura_do_arquivo` da lista no mesmo commit do conserto.
- D-795 "porque fazer isso?" · "porque ter um instalador pequeno então?" · "não tem nenhuma documentação dizendo para o
  que isso serve?" · "ok". Aqui: o Setup.exe é apagado no fim, também com erro; nunca vai ao rascunho do GitHub nem à
  pasta do servidor; a conferência do fim lê a pasta de saída e o destino.
- D-796 "não entendi" · "1, mas tem que ser explissito o pedido né". Aqui: sou implementador; não mexi em `ui/`.
- D-797 "Só precisa de dois lugares né?" · "ok". Aqui: trabalhei no meu ramo; quem junta é a gerente.
- D-798 "fechou". Aqui: não escrevo o rótulo de pronto.
- D-724 "gratis, mas o que é essa assinatura e é segura?". Aqui: o motor é assinado com a mesma chave e conferido pela
  mesma peça (`assinatura.py` não muda), com outro nome de pacote.
- D-727 "pode, se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador né". Aqui: o motor vai
  dentro do instalador, como um arquivo só.
- D-809 "ok". Aqui: o script lançado solto da peça apaga a pasta de troca sem seguir atalho, e o destino do
  publicar não apaga uma publicação que é atalho (pedido da gerente de 19/11, depois das regras novas).
- D-811 "ok". Aqui: a seção "Cada proteção e o teste que falha sem ela", provada numa cópia.
- D-812 "ok". Aqui: a seção "De onde vem cada dado da conferência".
- D-814 "ok". Aqui: não há pergunta ao Samuel nesta entrega (ver "Perguntas para o Samuel").
- D-807 "ok". Aqui: no PC, só os arquivos de teste que mexi, um por vez; o conjunto inteiro no GitHub.
- D-714 "1 - vamos seguir sua sugestão" · "2- ok". Aqui: publicar continua só quando alguém roda o comando.
- D-763 "ok, pode fazer". Aqui: o nome do pacote do motor é outro (EditorImpressaoMotorKraken) e não é o nome da pasta
  dos projetos.
- D-813 "ok". Aqui (volta 3): a recusa da peça lista o que o Windows aceita como programa (a documentação do
  CreateProcess e do subprocess, e o que foi rodado no PC) e compara a coisa de verdade (o arquivo completado pelo
  Windows e o começo dele), não o texto.
- D-815 "ok". Aqui: a volta 3 é de um agente novo, que começou por este formulário.

## O que já está escolhido e testado aqui

- `tests/test_empacotar.py`: o motor do jeito novo passa e o velho, com atalhos ou de outro protocolo, é recusado
  (`empacotar.conferir_motor_kraken`, com um motor de mentira SEM a ficha: por isso essa função não passou a exigir a
  ficha); `empacotar.achar_motor_kraken` pula o velho (troca `empacotar.LUGARES_DO_MOTOR`: o nome não pode mudar);
  faltando peça, para antes do PyInstaller; o Visual C++ oficial confere; `empacotar.assinatura_do_arquivo` roda de
  verdade num arquivo sem assinatura e o resultado não confere. Os testes do Inno continuam.
- `tests/test_decisoes_atualizacao.py`: D-714 (a versão de um lugar só; `empacotar.comando_do_vpk` com quatro
  argumentos tem `--packVersion`); D-724 (publicar sem a chave para antes de tudo, pelo `publicar(versao,
  destino_pasta=..., arquivo_da_chave=...)` e pelo `main(["--pasta", ..., "--chave", ...]) == 1`; a chave nunca dentro
  do repositório; o que o publicar assina o programa aceita); D-727 (`empacotar.comando_do_vpk` de fábrica tem `--msi`,
  `--instLocation PerMachine`, `--runtime win-x64` e nada de `--framework`; `empacotar.preparar_pasta_para_o_velopack`
  põe o Visual C++ em instalar\; `empacotar.esperados_no_pacote_do_velopack` e `empacotar.conferir_pacote_do_velopack`
  com peças cujo motor nem existe).
- `tests/test_decisoes_brasao.py` (o ícone no `vpk --icon`), `tests/test_nome_do_pacote.py` (o `--packId`, o
  `--packTitle`, o vpk preso na 1.2.161, `empacotar.nupkg_inteiro`).
- `tests/test_ocr_kraken.py`: `ocr_kraken.lugares_do_motor` tem pelo menos 2 lugares e `ocr_kraken.achar_pasta_do_motor`
  não quebra (o nome não pode mudar; e o defeito antigo nº 330, dos testes do motor que pulam calados numa cópia,
  continua, como o plano manda).
- `tests/test_windows_peca.py` e as conferências do porteiro (`tests/test_conferencias_codigo.py`,
  `tests/test_conferencias_excecoes.py`): a peça é fechada, o rodar genérico recusa o PowerShell, a lista de exceções
  só diminui.
- Livro: D-714, D-723, D-724, D-727, D-746, D-763, D-768, D-773, D-776, D-777, D-788 a D-790, D-795.
- **Nenhum desses testes mudou.** Todos passam (ver "Testes").

- **Volta 3:** nenhum teste antigo mudou no que ele cobra. A única mudança num teste antigo é a pedida pela gerente: o
  vpk de mentira deixou de ser um `vpk.cmd` (a peça passou a recusar o .bat e o .cmd) e virou um programa de prova de
  verdade (`tests/test_publicar_versao.py::_programa_de_prova`, o lançador do pip com o mesmo script). O teste antigo
  da janela do servidor (`test_o_que_nao_esta_numa_versao_liberada_e_recusado`, que cobra "não existe aqui (404)") foi
  respeitado: a frase nova só vale para o nome repetido.

## Como fica para quem usa e no livro

- **O Kaique: nada muda** na tela nem no livro (nenhum arquivo de `ui/` nem do processamento das páginas). O PDF que
  sai não muda, antes e depois. O que muda é o que ele vai baixar a partir do passo 3: a atualização sem o motor do
  Kraken (uns 460 MB em vez de 826 MB, conta do estudo) e, na primeira instalação, o .msi com o motor dentro como um
  arquivo só.
- **O Samuel, ao publicar (na prova à vista).** Antes: um comando que montava no D:, baixava a versão anterior, fazia
  a diferença, o .msi e o zip portátil, e liberava no GitHub antes de a assinatura subir. Depois: o mesmo comando; (1)
  primeiro diz quanto espaço vai usar no C: e para, com aviso, se o C: ficaria com menos de 20 GB livres; (2) monta no
  C:; (3) não baixa a versão anterior nem faz a diferença; (4) sobe como rascunho, lê de volta e só então libera; (5)
  no fim apaga o rascunho do C: e o Setup.exe, também quando dá erro, e lista o que ficou na pasta de saída e no
  destino. Para o motor, um comando próprio (`--motor`), raro. O .msi só com `--com-instalador`. Para apagar a versão
  de prova no fim: `--apagar v<versão>`.
- **O servidor das versões de prova:** uma janela pequena, com o endereço, as versões que ela serve e uma linha por
  pedido. Fechar a janela corta o que estiver sendo baixado (a internet caindo).
- **Problema novo criado:** a pasta que o publicar enche com `--pasta` agora tem uma subpasta por versão (como o
  GitHub). O jeito da etapa 5 de servir as versões direto de uma pasta (a fonte de teste do programa de hoje, que lê a
  pasta plana) não lê esse desenho: nas provas, as versões vêm pelo servidor (D-773), e o programa passa a falar com
  ele no passo 3. Escrito também em "Ressalvas".

- **Volta 3, para quem publica (o Samuel na prova):** nada muda no caminho que dá certo, fora duas linhas a mais na
  conferência do fim (o instalador "igual ao feito agora (tamanho e soma conferidos)", e no `--motor` a linha do
  rascunho). Muda o que se lê quando dá errado: (1) se a resposta do liberar se perder, a versão liberada fica e a
  frase diz "ficou liberada ... NÃO apaguei"; (2) se o .msi não couber na pasta de saída, nenhum .msi pela metade fica
  lá e a frase diz que a versão FOI publicada e que o instalador está inteiro na publicação; (3) o "PAREI" do fim
  aponta para a conferência do fim, em vez de dizer "foi apagado" sem conferir. Nenhum problema novo para o Kaique
  (nenhum arquivo do programa dele mudou de comportamento: a peça ainda não é usada por ele).

## A causa, a regra e todos os caminhos

**Por que os defeitos aconteciam (lista do plano, itens 53 a 57, e os do estudo):**
1. O vpk era rodado por dois caminhos, cada um do seu jeito (o `_rodar` do publicar com a pasta pronta e
   `empacotar.construir_pacote_do_velopack` com `subprocess.run`), e a pasta temporária vinha de quem chamava (a etapa 5
   a desviou à mão). Causa: não havia uma função que roda o vpk.
2. O PowerShell de `empacotar.assinatura_do_arquivo` falava com o Windows fora da peça única (item da lista de
   exceções).
3. O motor do Kraken ia dentro de toda versão (98% dos arquivos), porque a pasta portátil, a atualização e o instalador
   eram a mesma coisa.
4. No GitHub, o upload do vpk com publish liberava a versão antes de a assinatura subir (item 53): se a assinatura
   falhasse, a versão ficava liberada sem assinatura e o programa do Kaique a recusaria para sempre.
5. O Setup.exe e o rascunho ficavam (nada apagava) e a pasta pronta podia ser de outra versão (item 54).

**As regras, cada uma num lugar só:**
- Rodar o vpk: `empacotar.rodar_vpk` (a pasta temporária e a vigia do espaço).
- O comando do vpk: `empacotar.comando_do_vpk` (como hoje), com `--delta None` e `--noPortable` sempre, e o `--msi`
  só quando a saída pede.
- As três saídas (pasta portátil, atualização, instalador): `empacotar.SAIDAS`; tudo o que muda entre elas (motor
  solto, o motor-exigido.json, o arquivo do motor em instalar\, o .msi, o que o pacote tem de ter e não pode ter, a
  conta do espaço) lê dali.
- A conta do espaço e a reserva: `empacotar.espaco_que_vai_usar` e `empacotar.conferir_espaco`.
- O motor "inteiro e da versão certa": `ocr_kraken.conferir_motor` e a regra da ficha `ocr_kraken.conferir_ficha`
  (usada pela pasta e pelo arquivo do motor); a versão do motor: `ocr_kraken.VERSAO_DO_MOTOR`; a ficha é escrita só por
  `montar_motor_kraken.gravar_ficha_do_motor`; a forma do motor: `ocr_kraken.problemas_da_forma` (o empacotador a usa).
- Os nomes do motor publicado (pacote, etiqueta, arquivo) e a etiqueta da versão: `versao.py`.
- Ler a assinatura digital de um arquivo pelo Windows: `windows.ler_assinatura_digital` (função própria na peça).
- Publicar num destino (rascunho, enviar, ler de volta, liberar, apagar): `publicar_versao_kaique.publicar_arquivos`,
  sobre os dois destinos (`publicar_versao_kaique.DestinoPasta`, que o servidor serve, e
  `publicar_versao_kaique.DestinoGitHub`, pelo gh); a conversa com o GitHub, só em `DestinoGitHub._gh`.
- O que vai a um destino: `publicar_versao_kaique.arquivos_da_versao` (nunca o Setup.exe).
- O motor que a versão pede, lido de volta: `publicar_versao_kaique.obter_motor_publicado` (no começo, antes de liberar,
  e na leitura de volta da própria publicação do motor).

**Todos os caminhos (achados com busca no código: `vpk`, `comando_do_vpk`, `construir_pacote_do_velopack`,
`assinatura_do_arquivo`, `motor-kraken`, `LUGARES_DO_MOTOR`, `lugares_do_motor`, `conferir_motor_kraken`, `upload`):**
- `publicar_versao_kaique.publicar` (com e sem `--pasta-pronta`, com e sem `--com-instalador`) → `empacotar.rodar_vpk`
  pelo `empacotar.construir_pacote_do_velopack`.
- O download e o upload do vpk no publicar → saíram (sem diferença não há o que baixar; o envio é `publicar_arquivos`).
- `empacotar.preparar_vc_redist` → `empacotar.assinatura_do_arquivo` → `windows.ler_assinatura_digital`.
- `empacotar.construir_pasta` (a pasta portátil, o `--modo pasta`, o `--modo instalador` e o `--modo entrega` do Inno,
  e a atualização) → o motor solto só quando a saída diz.
- `montar_motor_kraken.main` (montar, `--so-servidor`, `--so-ficha`) → grava a ficha depois do teste e confere por
  `ocr_kraken.conferir_motor`.
- `publicar_versao_kaique.publicar_motor` → `ocr_kraken.conferir_motor` (a pasta) e `empacotar.problemas_do_zip_do_motor`
  (o arquivo), as duas pela mesma `ocr_kraken.conferir_ficha`.
- O programa (`ocr_kraken.achar_pasta_do_motor`, o teste rápido, o `--conferir-ocr`, o ajudante): **não mudam neste
  passo** (passo 3 do plano). `ocr_kraken.lugares_do_motor` continua igual.
- O servidor das versões lê a mesma pasta que `DestinoPasta` grava, pelas mesmas regras (`ETIQUETA_ACEITA` do publicar,
  `NOME_DO_INDICE` do empacotar), sem copiar.

**Volta 3 (relatório 2 de quem tentou quebrar). As causas e as regras, cada uma num lugar só:**
- *Versão liberada apagada (achado 1).* Causa: "só o rascunho é apagado" era decidido por uma leitura no
  `publicar_arquivos`, e o apagar lia de novo por conta própria e apagava o que achasse. Regra:
  `publicar_versao_kaique.apagar_publicacao(destino, etiqueta, so_rascunho=True)` lê ali dentro antes e depois, e
  chama `destino.apagar_rascunho`, que na pasta só toca na subpasta do rascunho (pela construção) e no GitHub lê de
  novo logo antes de pedir. Caminhos: o erro antes de liberar e o erro depois de pedir para liberar, na versão e no
  motor (os dois passam por `publicar_arquivos`) → `apagar_publicacao(so_rascunho=True)`; o `--apagar` →
  `apagar_publicacao` (apaga liberada, de propósito: o fim da prova).
- *O .msi pela metade (achado 2).* Causa: cópia direta no nome certo (`shutil.copyfile`, que não apaga o destino quando
  falha). Regra: a cópia conferida `empacotar.copiar_inteiro` (nome provisório, lida de volta: tamanho e soma, só então
  o nome certo; na falha apaga o pedaço e confere). Caminhos: o .msi para a pasta de saída
  (`publicar_versao_kaique.guardar_o_instalador`), o envio à pasta de destino (`DestinoPasta.enviar`) e a leitura de
  volta da pasta de destino (`DestinoPasta.baixar` → `baixar_vigiado`). (A cópia do motor para instalar\ do
  `empacotar.preparar_saida` não mudou: ela já confere a soma assinada e apaga o que não bate, e o `finally` do
  publicar tira o arquivo do motor de instalar\.)
- *O .bat e o .cmd pela peça (achado 3).* Causa: a recusa olhava onde o arquivo pedido mora, e não o que o Windows roda
  de verdade (um lote vai ao cmd.exe). Regra: `windows._programa_com_funcao_propria` → `windows._nao_e_programa_do_windows`
  (a extensão depois de o Windows completar o caminho, e o começo do arquivo, "MZ"). Caminhos: `windows.rodar_e_esperar`,
  `windows.lancar_solto`, `windows.abrir_em_grupo` (todos chamam a mesma regra).
- *O instante do grupo e a frase "conferido" (achados 4 e 9).* Causa: o programa nascia rodando e era posto no grupo
  depois; e a frase do fechar dependia de uma leitura que, sem resposta, virava "continua rodando". Regra:
  `windows.abrir_em_grupo` abre parado, põe no grupo, confere (IsProcessInJob) e só então solta
  (`windows._soltar_o_programa_parado`); `windows.ProgramaEmGrupo.fechar_tudo` só diz "conferido" com 0 vivos lidos.
  Caminho: `empacotar.rodar_vpk` (a vigia, o fim normal e o Ctrl+C) → `fechar_tudo`.
- *O motor baixado fora da conta e da vigia (achado 7).* Causa: a conta e a vigia só olhavam o vpk e a compressão; a
  vigia estava escrita duas vezes (no `rodar_vpk` e no `zipar_motor`). Regra: a vigia única `empacotar.vigia_do_espaco`
  (usada pelo `rodar_vpk`, pelo `zipar_motor`, pelo `copiar_inteiro` e pelo `DestinoGitHub._gh`); a conta
  `empacotar.espaco_que_vai_usar(..., baixado_para_o_rascunho=...)`. O nome "motor-kraken-": `versao.PREFIXO_DO_MOTOR`
  (a etiqueta aceita do publicar, o molde dos arquivos de motor em instalar\ e a lista do que não pode ir na
  atualização leem dali).
- *Textos (achado 8):* o cabeçalho da peça (quem a usa), o docstring do rascunho da pasta (as notas não são gravadas),
  a janela do servidor (`Versoes.procurar` diz por que não entrega) e a conta das "Ressalvas".

## O que pode falhar e o que o programa faz

| O que pode dar errado | O que o publicar faz |
|---|---|
| Sem licença de administrador | não precisa: nada do publicar pede licença (0 perguntas do Windows) |
| A pessoa diz "Não" | não há pergunta do Windows neste passo; não se aplica |
| Sem a chave, ou chave que não é a do programa | para antes de tudo (como hoje); nada é criado |
| A versão já foi publicada (ou sobrou um rascunho dela no destino) | para antes de montar, dizendo qual e como apagar o rascunho |
| O motor que a versão pede não está publicado, ou a assinatura dele não confere | para antes de montar: "publique o motor antes (--motor)" |
| Disco cheio antes (sobraria menos de 20 GB no C:) | para antes do vpk, dizendo quanto precisa e quanto há; o rascunho vazio é apagado |
| Disco cheio durante (outra coisa usando o C:) | a vigia vê o espaço cair abaixo da reserva, fecha o vpk que este comando abriu (só ele), o rascunho é apagado e a frase diz quanto ficou livre |
| O vpk falha ou não está instalado | para com o aviso; o rascunho é apagado |
| O pacote sai sem uma peça, ou com o motor dentro na atualização | para; o rascunho é apagado; nada vai ao destino |
| A pasta pronta é de outra versão, não tem a ficha, ou não tem o Visual C++ | para antes do vpk |
| Sem internet, ou o gh sem conta | para; se o rascunho do destino já tinha sido criado, é apagado e conferido; se não der para apagar, a frase diz o que ficou e o comando de apagar |
| O GitHub não responde ao perguntar se a versão existe | para (nunca vira "não existe") |
| A leitura de volta não bate (o arquivo no destino tem outra soma, ou a assinatura não confere) | não libera; apaga o rascunho do destino e confere |
| O Setup.exe | é apagado logo depois de cada vpk e o rascunho inteiro some no fim (também com erro); a conferência do fim lê a pasta de saída e o destino e diz se ele está lá |
| Arquivo preso (o antivírus lendo) ao apagar o rascunho | tenta de novo por alguns segundos; se ficar, diz o caminho e o tamanho do que ficou (nunca "apagado" sem conferir) |
| Arquivo preso por outro programa ao enviar | o envio falha → mesmo caminho da falha de internet |
| Desligar no meio (o PC ou a energia) | o rascunho fica no C: e o rascunho do destino fica sem liberar (nunca liberado pela metade); na próxima vez o comando acha o rascunho velho do destino e para dizendo como apagar; o rascunho velho do C: é apagado no começo da próxima vez (só as pastas com o nome do publicar) |
| O publicar roda dentro de um PowerShell 7 (terminal pwsh) | a peça abre o PowerShell do Windows sem a lista de módulos herdada: a assinatura do Visual C++ é lida igual (antes falhava com CouldNotAutoloadMatchingModule) |
| Um atalho (junção) dentro da pasta de troca do lançar solto, ou uma publicação do destino que é atalho | o lançar solto tira só o atalho e apaga o resto; o destino para sem apagar nada e diz que é atalho |
| O apagar de um rascunho no GitHub (o gh sai com erro mesmo tendo apagado, delete.go) | o rascunho é apagado sem pedir a etiqueta, e quem decide se apagou é a leitura de volta; o aviso do gh vai na frase |
| A vigia fecha o vpk com o WiX rodando (o .msi) | o vpk roda num grupo do Windows: fechar fecha ele, o cmd.exe e o wix.exe, e confere no Windows que nenhum ficou vivo; se ficou, a frase diz e manda olhar o Gerenciador de Tarefas |
| Erro do disco que não é dos previstos (pasta que não cria, arquivo preso ao somar, cópia do .msi) | a linha de comando diz "PAREI: o disco não deixou terminar (o arquivo): o motivo"; o rascunho já foi apagado pelo fim de cada caminho |
| A leitura depois de liberar falha | não apaga a versão liberada (achado 4); diz "liberada; não deu para reconferir agora" |
| Ctrl+C no meio | o mesmo caminho do erro: o vpk é fechado, o rascunho é apagado e o do destino também; a frase diz "interrompido" (sem a tela de erro do Python) |
| Dois publicar ao mesmo tempo | cada um tem o seu rascunho; o rascunho de outra vez só é apagado se tiver mais de 12 horas (antes, pode ser do outro rodando); a mesma versão no mesmo destino é recusada pelo segundo (já existe um rascunho) |
| O instalador pedido e a publicação falha depois | o .msi só vai para a pasta de saída depois de a versão estar publicada: um .msi de versão que não saiu nunca fica lá |
| O servidor: porta ocupada | a janela diz "NÃO ESTÁ SERVINDO" e o motivo, e não serve nada (a porta é exclusiva: outro servidor não abre a mesma) |
| O servidor: fechar no meio de um envio | corta a conexão de quem está baixando; quem baixa recebe menos do que o tamanho anunciado (o Velopack confere a soma e recusa) |
| O servidor: pedido de arquivo fora da pasta ("..", caminho com barra, o rascunho) | recusado (404), com a linha na janela |

| (volta 3) A resposta do liberar se perde e a leitura logo depois vem atrasada | a versão liberada nunca é apagada: o apagar só toca no rascunho, lido de novo na hora (na pasta, pela construção); a frase diz "ficou liberada ... NÃO apaguei" |
| (volta 3) O GitHub libera entre a leitura e o pedido de apagar (um instante) | fica o risco: o GitHub não tem "apague só se for rascunho" (Ressalvas) |
| (volta 3) A cópia do .msi para a pasta de saída falha (D: cheio, Ctrl+C) ou o publicar é fechado no meio | nenhum .msi com o nome certo fica pela metade (nome provisório); na falha o pedaço é apagado e conferido; a frase diz que a versão foi publicada e o instalador está na publicação; a conferência do fim compara o .msi da saída com o do rascunho |
| (volta 3) Um .bat ou .cmd (ou um lote com outro nome) pedido à peça | recusado antes de rodar ("este programa do Windows tem função própria na peça") |
| (volta 3) Um filho aberto no primeiro instante do vpk | não escapa: o vpk nasce parado e só é solto dentro do grupo |
| (volta 3) O Windows não responde à leitura do grupo depois de fechar | "não deu para conferir (o Windows não respondeu à leitura do grupo)", nunca "conferido" nem "continua rodando" |
| (volta 3) O C: cai abaixo da reserva enquanto o motor é baixado para o instalador | a vigia para o download (a cópia da pasta ou o gh), o segundo vpk não roda, o rascunho é apagado |
| (volta 3) A segunda pasta de troca do lançar solto não nasce | a primeira é apagada na hora |

## O que li da peça de fora e onde

Código do Velopack na etiqueta 1.2.161 (commit `92d6a1c9`, MIT), cópia só para ler em
`D:\programas\EditorImpressao\saida_teste\publicar-rapido\fonte-velopack\repo`:
- `src/vpk/Velopack.Packaging/PackageBuilder.cs:60` a 190: o vpk pack lê a versão anterior da pasta de saída só para a
  diferença (com `--delta None` não a faz); se a pasta de saída já tem versão igual ou maior, **pergunta** ("Do you want
  to continue...?"): por isso a pasta de saída é sempre nova; o portátil só sai sem `--noPortable`; o Setup.exe sai
  sempre que não houver `--noInst`; no fim move tudo para a pasta de saída e grava a lista dos arquivos
  dele, o índice das versões e o RELEASES antigo.
- `src/vpk/Velopack.Packaging/PackOptionsValidator.cs:19`: "Cannot use 'noPortable' and 'noInst' options together"
  (por isso o Setup.exe sempre sai, D-795).
- `src/vpk/Velopack.Vpk/Commands/Packaging/PackCommand.cs:89` a 117: `--delta` (de fábrica `BestSpeed`),
  `--noPortable` e `--noInst` (escondidos); `src/vpk/Velopack.Vpk/Commands/Packaging/WindowsPackCommand.cs:101`:
  `--msi`.
- `src/vpk/Velopack.Packaging.Windows/Commands/WindowsPackCommandRunner.cs:200` a 252: o Setup.exe leva o pacote
  inteiro dentro; o .msi copia a pasta do programa outra vez e a comprime (não leva o pacote).
- `src/vpk/Velopack.Core/DefaultName.cs:5` a 63: os nomes `<id>-<versao>-full.nupkg`, `<id>-win-Setup.exe`,
  `<id>-win.msi`, `<id>-win-Portable.zip` (o sufixo é "-" mais o canal, "win"). Conferido na pasta da etapa 5
  (`D:\programas\EditorImpressao\saida_teste\etapa5\servidor`): os mesmos nomes.
- `src/lib-csharp/Util/TempUtil.cs:20` a 45: a pasta temporária do vpk é a da variável VELOPACK_TEMP, senão
  TMPDIR, TEMP ou TMP mais "velopack". Por isso `empacotar.rodar_vpk` dá ao vpk as três dentro do rascunho.
- `src/vpk/Velopack.Core/BuildAssets.cs:72` e `src/vpk/Velopack.Deployment/_GitRelease.cs:213` a 262: o upload do vpk
  para o GitHub envia **todos** os arquivos da lista (inclusive o Setup.exe) e falha se faltar um; com publish, libera
  logo depois de enviar. `src/vpk/Velopack.Deployment/Local.cs:115` e `_ObjectStore.cs:215`: o upload para uma pasta
  também envia todos. Por isso o publicar não usa mais o upload do vpk (o Setup.exe chegaria ao rascunho do GitHub,
  contra a D-795, e a liberação viria antes da assinatura).
- `src/vpk/Velopack.Packaging/ReleaseEntryHelper.cs:100` a 134: o índice da pasta de saída lista os pacotes da pasta
  (com a pasta nova, só esta versão) com a soma SHA-256 e o tamanho; é o mesmo formato que o upload envia.
- Do lado do programa, `src/lib-rust/src/sources/http.rs:42` a 70 e `src/lib-rust/src/sources/mod.rs:64`: um endereço
  http:// vira a fonte HTTP, que pede o índice com "?localVersion=...&id=...&stagingId=..." e baixa
  "<endereço>/<FileName>". É o que o servidor das versões responde.

**Lido na volta 2:** https://github.com/cli/cli/blob/trunk/pkg/cmd/release/delete/delete.go (deleteRun e deleteTag):
o gh apaga a publicação e, com `--cleanup-tag`, apaga depois a etiqueta sem olhar se é rascunho, e devolve o erro dessa
segunda parte; num rascunho a etiqueta não existe. Microsoft Learn, https://learn.microsoft.com/windows/win32/procthread/job-objects
e AssignProcessToJobObject: o que um processo do grupo cria entra no grupo; TerminateJobObject fecha todos; com
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE, fechar a última alça fecha todos; grupos dentro de grupos desde o Windows 8. O vpk:
`src/vpk/Velopack.Packaging.Windows/Msi/MsiBuilder.cs:221` (o .msi sai de `Exe.RunHostedCommand`, que abre
cmd.exe e wix.exe), `src/vpk/Velopack.Packaging/PackageBuilder.cs:76` (a pasta temporária vive até o fim do pack) e
`src/vpk/Velopack.Packaging.Windows/Commands/WindowsPackCommandRunner.cs:231` (a cópia a mais do .msi).

O gh 2.99.0 (instalado no PC), código `cli/cli`, https://github.com/cli/cli/blob/trunk/pkg/cmd/release/shared/fetch.go
(lido em 19/11): `FetchRelease` acha uma publicação liberada pela etiqueta ou um rascunho pela etiqueta pendente; sem
nenhuma, o erro "release not found". Os campos de `--json` incluem `isDraft` e `assets` (cada um com `name`, `size` e
`digest`). `gh release download <etiqueta> --pattern <nome> --dir <pasta>` baixa (vale para rascunho).

Microsoft Learn, https://learn.microsoft.com/dotnet/api/system.management.automation.signaturestatus: os estados de
`Get-AuthenticodeSignature` são Valid, UnknownError, NotSigned, HashMismatch, NotTrusted, NotSupportedFileFormat e
Incompatible; "Valid" diz só que a assinatura é válida (quem assinou, o nosso `empacotar.vc_redist_confere` confere).
Conferido rodando: o PowerShell do Windows dá "Valid" com a Microsoft; um script sem assinatura dá "NotSigned"; um
arquivo que começa com "MZ" e não é programa dá "UnknownError".

Python 3.14, https://docs.python.org/3/library/: `shutil.disk_usage` (o espaço livre do disco de uma pasta);
`subprocess.Popen.kill` (fecha só o processo que abrimos); `zipfile` (confere a soma de cada arquivo ao abrir,
`Lib/zipfile/__init__.py:1115`, estudo do Kraken §3); `http.server.ThreadingHTTPServer` (a documentação avisa que não
é para servidor de produção: aqui só escuta em 127.0.0.1, na prova). **Achado rodando:** o http.server liga de fábrica
o "reusar o endereço" (`Lib/http/server.py:135`, `allow_reuse_address = True`), e no Windows isso deixou um segundo
servidor abrir a mesma porta sem erro; o servidor das versões desliga isso e pede a porta exclusiva (SO_EXCLUSIVEADDRUSE,
https://learn.microsoft.com/windows/win32/winsock/using-so-reuseaddr-and-so-exclusiveaddruse).

Microsoft Learn, https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_psmodulepath?view=powershell-5.1
(lido em 19/11, depois da rodada 1 do GitHub): o PowerShell do Windows monta a lista de módulos ao abrir; sem a
variável PSModulePath, usa a de fábrica; e a nota "Inherited PowerShell 7 module paths precede the Windows PowerShell
system module path [...] This breaks module autoloading". Refeito no PC com um módulo que não carrega na frente da
lista: o mesmo CouldNotAutoloadMatchingModule do GitHub.

**Deduzido, não lido:** que o vpk não deixa programa rodando depois de ser fechado à força pela vigia (o .msi roda o
WiX por dentro; se sobrar um, o rascunho não apaga e a frase diz o que ficou).

**Lido e rodado na volta 3 (20/11/2026):**
- Microsoft Learn, CreateProcessW (https://learn.microsoft.com/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw):
  o módulo é "a Windows-based application" ou "some other type of module (for example, MS-DOS or OS/2) if the
  appropriate subsystem is available"; "To run a batch file, you must start the command interpreter"; sem extensão,
  ".exe is appended"; a busca do nome sozinho: a pasta do programa que chama, a pasta atual, System32, System, Windows,
  o PATH. Python 3.14, subprocess, "Security Considerations": "On Windows, batch files (*.bat or *.cmd) may be launched
  by the operating system in a system shell regardless of the arguments passed to this library"; e "when resolving or
  searching for the executable path with shell=False, cwd does not override the current working directory".
- **Rodado no PC** (`relatorios/passo2-publicar/anexos/variantes-do-lote-resultado.txt:1`; subprocess sem shell, um lote que escreve a COMSPEC): "x.bat", "X.BAT" e "x.bat " rodaram pelo
  cmd.exe; "x.bat." e o prefixo de caminho longo abriram algo que saiu com código 1; "x.bat::$DATA" deu o erro 193; um
  lote com nome de .exe e um .bat que começa com "MZ" deram o erro 216 (não rodaram). Conclusão: o Windows só entrega
  ao cmd.exe o que não começa com "MZ" e tem extensão de lote. **Deduzido, não lido:** que o mesmo vale para o
  `CreateProcess` chamado de outro jeito (só o do subprocess foi rodado).
- Microsoft Learn, Process Creation Flags (https://learn.microsoft.com/windows/win32/procthread/process-creation-flags): CREATE_SUSPENDED: "The primary thread of the new process is created in a
  suspended state, and does not run until the ResumeThread function is called". CREATE_NO_WINDOW: "The process is a
  console application that is being run without a console window" (achado 10).
- Microsoft Learn, AssignProcessToJobObject (https://learn.microsoft.com/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject): "By default, all child processes are associated with the immediate job
  and every job in the parent job chain"; "The child process breaks away from every job in the job chain unless a job
  in the chain does not allow breakaway". "Job Objects" (https://learn.microsoft.com/windows/win32/procthread/job-objects): "Child processes created using Win32_Process.Create are not
  associated with the job" (o vpk não usa o WMI); "closing the last job object handle terminates all associated
  processes" (com KILL_ON_JOB_CLOSE).
- O `IsProcessInJob` (https://learn.microsoft.com/windows/win32/api/jobapi/nf-jobapi-isprocessinjob) pede uma alça com licença de leitura do processo: sem ela, o Windows respondeu "acesso negado"
  (erro 5), achado rodando; a alça passou a pedir PROCESS_QUERY_LIMITED_INFORMATION.
- Python 3.14, `Lib/subprocess.py:1575` (`_execute_child`, na cópia do PC): o subprocess fecha a alça da linha
  principal (`_winapi.CloseHandle(ht)`) e não guarda o número dela; por isso a peça a acha pela foto das linhas do
  Windows (CreateToolhelp32Snapshot, TH32CS_SNAPTHREAD, Thread32First/Next) e a solta com ResumeThread.
  `Popen.communicate` com tempo: "Catching this exception and retrying communication will not lose any output" (a vigia
  do gh).
- O lançador do pip (`.venv/Lib/site-packages/pip/_vendor/distlib/scripts.py:259`, `_write_script`, até a linha 278): o .exe é
  "launcher + shebang + zip_data", com o `__main__.py` no zip. É o vpk de mentira dos testes.
- GitHub, a API de apagar uma publicação (https://docs.github.com/rest/releases/releases#delete-a-release): recebe só o número da publicação, sem condição (lembrado; não relido nesta
  volta): por isso fica o instante da Ressalva.

## O que foi feito

1. **A assinatura digital pela peça única** (`windows.ler_assinatura_digital`, nova): o empacotar deixou de abrir o
   PowerShell por conta própria para ler a assinatura do Visual C++. O item saiu da lista de exceções (176 → 175), no
   mesmo commit.
2. **As três saídas num lugar só** (`empacotar.SAIDAS`): a pasta portátil (com o motor solto, como sempre), a
   atualização (sem o motor, com o motor-exigido.json) e o instalador (com o arquivo do motor publicado em instalar\ e
   o .msi). O pacote da atualização com o motor solto é recusado.
3. **Uma função roda o vpk** (`empacotar.rodar_vpk`): a pasta temporária no rascunho e a vigia do espaço; o comando sem
   a diferença e sem o zip portátil; o .msi só no instalador; o Setup.exe apagado na hora.
4. **A conta do espaço e a reserva de 20 GB** (`empacotar.espaco_que_vai_usar`, `empacotar.conferir_espaco`): antes do
   vpk e durante.
5. **O motor à parte, na parte que o publicar usa:** a versão do motor (`ocr_kraken.VERSAO_DO_MOTOR` = 1), a ficha
   motor.json gravada pelo montar depois do teste (`--so-ficha` para o motor que já existe), a conferência única
   (`ocr_kraken.conferir_motor` e `ocr_kraken.conferir_ficha`), o arquivo do motor comprimido e conferido
   (`empacotar.zipar_motor`), os nomes em `versao.py`.
6. **O publicar refeito:** o rascunho no C:; dois destinos (uma pasta com uma subpasta por versão, e o GitHub pelo gh)
   com o mesmo caminho (rascunho, enviar só o pacote, o índice e a assinatura, ler de volta, só então liberar; falha
   apaga o rascunho do destino); antes, o motor que a versão pede tem de estar publicado e conferir; `--motor` publica
   o motor; `--com-instalador` faz o .msi numa segunda passada do vpk (o publicado é sempre o pacote da atualização) e
   o .msi vai à publicação e à pasta de saída; `--apagar` apaga uma publicação e confere; no fim, sempre, a conferência
   do rascunho, da pasta de saída, do destino e do Setup.exe. A ficha da versão na pasta montada recusa a pasta pronta
   de outra versão.
7. **Conserto na peça do Windows (bug que impedia a tarefa):** o PowerShell aberto pela peça herdava a lista de
   módulos do PowerShell 7 (no Windows do GitHub, ou num terminal pwsh) e não carregava os dele; a assinatura digital
   nunca era lida lá. Agora a peça o abre sem essa lista (`_ambiente_do_powershell`, lugar único, ao lado do comando
   do PowerShell), no rodar e esperar e no lançar solto.
8. **Volta 2 (os achados de quem tentou quebrar):** o apagar no GitHub certo para rascunho e para liberada, decidido
   pela leitura de volta; o vpk num grupo do Windows (`windows.abrir_em_grupo`), que a vigia e o Ctrl+C fecham inteiro;
   nada apagado depois de pedir para liberar; o erro do disco em frase; o lançar solto sem "saiu sem começar"; o .msi
   com o número da versão e o servidor sem nome repetido nem junção (a regra das publicações num lugar só); o motor em
   instalar\ recusado na atualização; a conta do espaço refeita; a etiqueta conferida inteira.
9. **O servidor das versões de prova** (`servidor_das_versoes.py`, novo): a janela, o índice de todas as versões
   liberadas, os arquivos pelo nome, o rascunho escondido, fechar corta o envio, `--limite` deixa lento, a porta
   exclusiva.

10. **Volta 3 (os achados do relatório 2):** só o rascunho apagado no caminho de erro; a cópia conferida para o .msi e
   para a pasta de destino; a conferência do fim compara o .msi; a peça recusa o lote; o programa do grupo nasce parado;
   a frase do fechar só com o grupo lido; o motor baixado na conta e na vigia; a vigia num lugar só; o nome do motor
   num lugar só; os textos que não batiam; o vpk de mentira como programa de verdade.

## Arquivos criados ou alterados

- `core/windows.py`
- `empacotar.py`
- `publicar_versao_kaique.py`
- `montar_motor_kraken.py`
- `core/ocr_kraken.py`
- `versao.py`
- `servidor_das_versoes.py` (novo)
- `tests/test_windows_peca.py` (3 testes novos; nenhum antigo mudou)
- `tests/test_publicar_versao.py` (novo)
- `tests/test_publicar_motor.py` (novo)
- `tests/test_publicar_servidor.py` (novo)
- `tests/conferencias_excecoes.json` (o item consertado saiu, pelo `python -m regras_dos_agentes excecoes --diminuir`;
  fora da lista do pedido: o porteiro avisa, K14; é o "tire esse item da lista no mesmo commit" do pedido)
- `relatorios/passo2-publicar/` (este formulário e os anexos)

- `relatorios/passo2-publicar/anexos/reversao-volta3-codigo-antigo.txt`, `relatorios/passo2-publicar/anexos/reversao-volta3-resultado.txt`,
  `relatorios/passo2-publicar/anexos/reversao-volta3-mutacoes.py.txt`, `relatorios/passo2-publicar/anexos/variantes-do-lote.py.txt`,
  `relatorios/passo2-publicar/anexos/variantes-do-lote-resultado.txt` e `relatorios/passo2-publicar/anexos/lote-que-comeca-com-mz.py.txt`
  (volta 3: o resultado no código antigo, as mutações, o script e o ensaio dos jeitos de escrever um lote)

## Como cumpri cada uma

- D-767: o defeito da lista de módulos só apareceu rodando de verdade (no GitHub) e foi refeito de verdade no PC antes
  de consertar (`tests/test_windows_peca.py::test_o_powershell_nao_herda_os_modulos_do_powershell_7`).
  Nada rodou de verdade no Windows além de ler (a assinatura digital, o espaço do disco); o vpk e o GitHub dos
  testes são de mentira e os testes dizem isso no cabeçalho; o de verdade fica para a prova à vista ("A prova de
  verdade").
- D-768: o pacote da atualização sai sem o motor e é conferido sem ele
  (`tests/test_publicar_versao.py::test_d768_o_motor_e_a_versao_publicados_numa_pasta_sem_o_motor_no_pacote`,
  `tests/test_publicar_versao.py::test_d768_o_pacote_da_atualizacao_com_o_motor_solto_e_recusado`).
- D-773: o servidor das versões (`tests/test_publicar_servidor.py::test_d773_o_indice_junta_as_versoes_liberadas_e_nao_mostra_o_rascunho`,
  `tests/test_publicar_servidor.py::test_d773_fechar_e_a_internet_caindo_no_meio_do_download`); o rascunho no GitHub
  (`tests/test_publicar_versao.py::test_o_github_sobe_como_rascunho_le_de_volta_e_so_entao_libera`, com o gh de
  mentira) e o `--apagar`.
- D-775: entrego à gerente sem rótulo, para quem tenta quebrar.
- D-776: `tests/test_publicar_versao.py::test_d776_sem_espaco_para_antes_do_vpk_e_nada_fica`,
  `tests/test_publicar_versao.py::test_d776_a_vigia_fecha_o_vpk_quando_o_disco_cai_abaixo_da_reserva`,
  `tests/test_publicar_versao.py::test_d776_a_conta_do_espaco_e_a_reserva_de_20_gb`,
  `tests/test_publicar_motor.py::test_d776_comprimir_o_motor_para_quando_o_disco_cai_abaixo_da_reserva`.
- D-777: `tests/test_publicar_versao.py::test_d789_d777_o_comando_do_vpk_sem_diferenca_sem_portatil_e_o_msi_so_quando_pedido`,
  `tests/test_publicar_versao.py::test_d777_o_instalador_so_quando_pedido_e_o_publicado_e_o_da_atualizacao`.
- D-785: nada pesado montado, nada publicado; a janela do servidor só foi aberta fora da tela, nos testes.
- D-786: o caminho do livro não usa nada do que mudou (ver "Velocidade").
- D-788: o arquivo do motor em instalar\ só no instalador (`tests/test_publicar_motor.py::test_o_motor_exigido_diz_o_motor_publicado`).
- D-789: `--delta None` e nenhum download da versão anterior (o mesmo teste da D-777 confere o comando de cada vez
  que o vpk rodou).
- D-790: `tests/test_publicar_versao.py::test_d790_sem_o_motor_publicado_nada_e_montado` e, antes de liberar, o motor
  lido de novo (`tests/test_publicar_versao.py::test_n1_n3_n4_n14_cada_leitura_de_volta_errada_impede_liberar`, o caso
  "motor sumiu"). **Correção da volta 2:** a primeira entrega dizia que o `test_d53` provava isso; não provava (ele só
  cobra a ordem; quem tentou quebrar desligou a leitura de novo do motor e ele passou).
- D-791: o item saiu da lista no commit do conserto (`0d844b4f`); o porteiro passou no GitHub ("Testes").
- D-795: `tests/test_publicar_versao.py::test_d795_o_setup_exe_e_o_rascunho_somem_tambem_quando_da_erro` (com erro) e
  o teste da D-768 (sem erro): o Setup.exe nunca está no destino nem na pasta de saída, e a conferência do fim diz isso.
- D-796: nenhum arquivo de `ui/` mudou.
- D-797: tudo no ramo `passo2-publicar-2026-11-19`.
- D-798: nenhum rótulo de pronto neste ramo.
- D-724: `tests/test_publicar_versao.py::test_d724_o_motor_com_a_assinatura_de_outra_chave_e_recusado`; `assinatura.py`
  não mudou.
- D-727: o motor dentro do instalador (o teste da D-777 confere a segunda passada com o arquivo do motor).
- D-809: `tests/test_windows_peca.py::test_o_lancado_solto_apaga_a_pasta_de_troca_sem_seguir_atalho` e
  `tests/test_publicar_versao.py::test_d809_apagar_uma_publicacao_que_e_atalho_nao_apaga_o_outro_lado`; as junções
  dos testes nascem e saem em pastas temporárias do próprio teste, com o outro lado conferido inteiro depois.
- D-811: a seção "Cada proteção e o teste que falha sem ela" (19 de 19 na primeira entrega; na volta 2, mais 21, das
  quais 20 acusadas sozinhas e uma dupla proteção escrita).
- D-812: a seção "De onde vem cada dado da conferência" (os dois dados que o conferido escreve estão marcados como
  não-prova).
- D-814: nenhuma pergunta ao Samuel; procurei antes no Livro (ver "Perguntas para o Samuel").
- D-807: no PC, um arquivo de teste por vez (lista em "Testes"); o conjunto inteiro no GitHub.
- D-714: o publicar só roda pelo comando; nada liga sozinho.
- D-763: `tests/test_publicar_motor.py::test_d763_o_nome_do_pacote_do_motor_e_outro_e_nao_e_pasta_de_dados`.

- **Volta 3:** D-776 (a conta soma o motor baixado e a vigia vigia o download:
  `tests/test_publicar_versao.py::test_volta3_achado7_o_motor_baixado_entra_na_conta_e_na_vigia`,
  `tests/test_publicar_versao.py::test_volta3_achado7_o_gh_que_baixa_e_fechado_pela_vigia`); D-795 (a conferência do fim
  continua dizendo do Setup.exe; o .msi ganha a sua linha:
  `tests/test_publicar_versao.py::test_volta3_achado2_o_msi_da_pasta_de_saida_e_comparado_com_o_do_rascunho`); D-767 (o
  grupo, o lote e a cópia cortada rodam de verdade:
  `tests/test_windows_peca.py::test_o_programa_nasce_parado_e_so_roda_dentro_do_grupo`,
  `tests/test_windows_peca.py::test_bat_e_cmd_sao_recusados_pelo_rodar_pelo_lancar_e_pelo_grupo`,
  `tests/test_publicar_versao.py::test_volta3_a_copia_cortada_no_meio_nunca_deixa_o_nome_certo`); D-811 (24 de 24
  proteções acusadas, `anexos/reversao-volta3-resultado.txt`); D-812 (a seção "De onde vem cada dado", acrescentada);
  D-813 (o que o Windows aceita como programa, em "O que li", e a recusa pelo arquivo de verdade); D-815 (agente novo,
  começou por este formulário); D-798 (nenhum rótulo de pronto); D-809 (nenhuma junção nesta volta).

## Testes

- **No PC, um arquivo por vez** (19/11, com `QT_QPA_PLATFORM=offscreen`):
  `tests/test_publicar_versao.py` 20 passaram; `tests/test_publicar_motor.py` 12; `tests/test_publicar_servidor.py` 11
  (três vezes seguidas, para ver se o corte no meio é estável); `tests/test_windows_peca.py` 55 passaram e 2 pulados (os
  que só rodam no GitHub); `tests/test_empacotar.py` 41; `tests/test_decisoes_atualizacao.py` 38;
  `tests/test_decisoes_brasao.py` 22; `tests/test_nome_do_pacote.py` 5; `tests/test_ocr_kraken.py` 27 e 6 pulados (o
  motor não está nesta cópia, o defeito antigo nº 330); `tests/test_ocr_diagnostico.py` 6;
  `tests/test_windows_janela_de_prova.py` 10; `tests/test_conferencias_codigo.py` 77; `tests/test_conferencias_pacote.py`
  20; `tests/test_conferencias_excecoes.py` 14. Porteiro no PC: "nada novo" (175 lugares).
- **Prova de reversão** numa cópia à parte (git archive no rascunho da sessão, fora do projeto): 19 de 19 proteções
  acusadas pelo seu teste (`anexos/reversao-resultado.txt`, script em `anexos/reversao-mutacoes.py.txt`); os testes
  novos rodados no código antigo falham (`anexos/reversao-codigo-antigo.txt`).
- **No GitHub, rodada 1:** 44642471223, sobre o commit 2e88d125: **failure**. O porteiro passou (PORTEIRO: success,
  o trabalho "Porteiro (juiz da versao de teste)"); as partes 1 a 4 e os botões passaram; na parte 5 falhou
  `tests/test_windows_peca.py::test_a_assinatura_digital_e_lida_pela_peca_de_verdade` (CouldNotAutoloadMatchingModule:
  o defeito da lista de módulos herdada do PowerShell 7, consertado em `fa28ab5b`). As rodadas 44644159110 e
  44644488805 foram canceladas por mim (testavam commits já passados).
- **No PC, depois do conserto:** `tests/test_windows_peca.py` 54 passaram e 2 pulados; o teste novo da lista de
  módulos falhou antes do conserto (CouldNotAutoloadMatchingModule) e passa depois.
- **No GitHub, rodada 4:** 44645740920, sobre o commit fa28ab5b (o conserto da lista de módulos): **success**, todas
  as partes e os botões. PORTEIRO: success (o trabalho "Porteiro (juiz da versao de teste)").
- **Volta 2, no PC, um arquivo por vez** (19-20/11): `tests/test_publicar_versao.py` 36 passaram;
  `tests/test_publicar_servidor.py` 13; `tests/test_publicar_motor.py` 12; `tests/test_windows_peca.py` 57 e 2 pulados;
  `tests/test_empacotar.py` 41; `tests/test_decisoes_atualizacao.py` 38; `tests/test_windows_janela_de_prova.py` 10;
  `tests/test_conferencias_codigo.py` 77; `tests/test_nome_do_pacote.py` 5. Porteiro no PC: "nada novo" (175).
  Reversão: `anexos/reversao-volta2-resultado.txt`.
- **No GitHub, volta 2, rodada final:** 44663876080, sobre o ramo em 0d51ad5e: **success** na primeira tentativa, todas
  as partes e os botões. PORTEIRO: success (o trabalho "Porteiro (juiz da versao de teste)").
- **No GitHub, volta 2, rodada anterior:** 44661337397, sobre 0f7639eb: **failure**. PORTEIRO: success. Falharam
  `tests/test_publicar_versao.py::test_achado5_erro_do_disco_vira_frase` (o teste supunha o vpk instalado, como no PC;
  no Windows do GitHub não há vpk e a linha de comando parava antes; consertado no teste em `0d51ad5e`, família F4) e
  `tests/test_decisoes_so_as_letras.py::test_d148_desfazer_o_automatico_devolve_o_so_as_letras_do_livro` (o instável
  conhecido, por tempo; não é deste passo).
- **No GitHub, rodada final da volta 1:** 44650408369, sobre o ramo em a14b7d55 (o código de 0ef0da17; depois só o formulário):
  **success** na segunda tentativa (só a parte 3 rodou de novo). PORTEIRO: success (o trabalho "Porteiro (juiz da
  versao de teste)"). Na primeira tentativa falhou só
  `tests/test_decisoes_gravura_a_mao.py::test_d659_g_outros_filtros_a_mao_nada_e_procurado_e_sai_igual_ao_de_antes`
  ("procurou: [0]"), o teste instável já conhecido (catálogo P1-gh-5), que não usa nada deste passo.

- **Volta 3, no PC, um arquivo por vez** (20/11, `QT_QPA_PLATFORM=offscreen`): `tests/test_publicar_versao.py` 49
  passaram; `tests/test_windows_peca.py` 62 passaram e 2 pulados; `tests/test_publicar_servidor.py` 14;
  `tests/test_publicar_motor.py` 12; `tests/test_empacotar.py` 41; `tests/test_decisoes_atualizacao.py` 38;
  `tests/test_nome_do_pacote.py` 5; `tests/test_decisoes_brasao.py` 22; `tests/test_windows_janela_de_prova.py` 10;
  `tests/test_ocr_kraken.py` 27 e 6 pulados; `tests/test_conferencias_codigo.py` 77; `tests/test_conferencias_excecoes.py`
  14; `tests/test_conferencias_pacote.py` 20. Porteiro no PC: "nada novo" (175 lugares). (Uma vez rodei dois arquivos
  juntos, por engano: `test_publicar_versao.py` e `test_publicar_motor.py`; depois, só um por vez.)
- **Volta 3, reversão:** os testes novos no código da volta 2 (9cd555a5): falham os 15 do defeito consertado
  (`anexos/reversao-volta3-codigo-antigo.txt`); passam lá os dos achados 5 e 6 e o do soltar do grupo, que cobram
  proteções que já existiam e são provados pela mutação (B5, B6, B4b).
- **No GitHub, volta 3:** rodada 44675872042, sobre o ramo em 2e906e94 (o código de e4263c0a e três docstrings de um
  teste). Resultado: ainda rodando na entrega (o porteiro e as partes ver abaixo, na entrega à gerente); a gerente confere o fim. A rodada 44675045916, sobre 05f743ca, foi cancelada por mim aos 7 minutos (o
  porteiro já tinha dado success), porque depois dela mudaram um comentário da peça e as docstrings.

## Caminho e função

- O publicar da versão, com ou sem pasta pronta, com ou sem instalador → `empacotar.construir_pacote_do_velopack` →
  `empacotar.rodar_vpk` (prova: `tests/test_publicar_versao.py::test_d777_o_instalador_so_quando_pedido_e_o_publicado_e_o_da_atualizacao`,
  as duas passadas pelo mesmo caminho).
- Os dois destinos → `publicar_versao_kaique.publicar_arquivos` (prova: o mesmo fluxo na pasta,
  `tests/test_publicar_versao.py::test_d53_nada_e_liberado_antes_da_assinatura_lida_de_volta`, e no GitHub,
  `tests/test_publicar_versao.py::test_o_github_sobe_como_rascunho_le_de_volta_e_so_entao_libera`).
- A versão do programa e o motor → `publicar_versao_kaique.publicar_arquivos` e `publicar_versao_kaique.obter_motor_publicado`
  (os dois testes acima publicam os dois).
- A pasta do motor e o arquivo do motor → `ocr_kraken.conferir_ficha` (prova:
  `tests/test_publicar_motor.py::test_o_arquivo_do_motor_leva_tudo_da_ficha_e_e_conferido` e
  `tests/test_publicar_motor.py::test_o_motor_estragado_ou_de_outra_versao_nao_confere`).
- A forma do motor no empacotador e no programa → `ocr_kraken.problemas_da_forma` (prova:
  `tests/test_publicar_motor.py::test_o_empacotador_usa_a_forma_do_motor_do_lugar_unico`).
- O que o vpk escreve e o que vai ao destino → `publicar_versao_kaique.arquivos_da_versao` (prova: o teste da D-768).
- Todo PowerShell que a peça abre (o rodar e esperar, o lançar solto, os scripts do trabalho com licença) → o mesmo
  comando e o mesmo ambiente (`_comando_do_powershell`, `_ambiente_do_powershell`; prova:
  `tests/test_windows_peca.py::test_o_powershell_nao_herda_os_modulos_do_powershell_7`, pelo rodar e pelo lançar solto).
- A assinatura digital do Visual C++ → `windows.ler_assinatura_digital` (prova:
  `tests/test_windows_peca.py::test_o_empacotar_le_a_assinatura_pela_peca_e_nao_abre_o_powershell`).
- O servidor e o publicar na pasta → o mesmo desenho (`DestinoPasta` grava; o servidor lê pelas mesmas regras; prova:
  `tests/test_publicar_servidor.py::test_d773_o_indice_junta_as_versoes_liberadas_e_nao_mostra_o_rascunho`, que monta a
  pasta pelo próprio `DestinoPasta`).

- **Volta 3:** só o rascunho apagado → `apagar_publicacao(so_rascunho=True)` (prova, os dois destinos pelo mesmo caminho:
  `tests/test_publicar_versao.py::test_volta3_achado1_uma_leitura_atrasada_depois_de_liberar_nunca_apaga_a_versao_liberada`
  e `tests/test_publicar_versao.py::test_volta3_achado1_no_github_a_leitura_atrasada_tambem_nunca_apaga_a_liberada`); as
  três cópias do publicar → `empacotar.copiar_inteiro` (prova:
  `tests/test_publicar_versao.py::test_volta3_achado2_o_msi_que_nao_termina_de_copiar_nao_fica_com_o_nome_certo` e os
  testes antigos do envio à pasta); o rodar, o lançar e o grupo → `windows._programa_com_funcao_propria` (prova: o mesmo
  lote recusado pelos três, `tests/test_windows_peca.py::test_bat_e_cmd_sao_recusados_pelo_rodar_pelo_lancar_e_pelo_grupo`);
  a vigia do vpk, da compressão, da cópia e do gh → `empacotar.vigia_do_espaco` (prova: os testes antigos da vigia do vpk
  e da compressão continuam, e
  `tests/test_publicar_versao.py::test_volta3_achado7_o_motor_baixado_entra_na_conta_e_na_vigia` e
  `tests/test_publicar_versao.py::test_volta3_achado7_o_gh_que_baixa_e_fechado_pela_vigia`); o nome do motor →
  `versao.PREFIXO_DO_MOTOR` (prova: `tests/test_publicar_versao.py::test_volta3_achado7_o_nome_do_motor_so_em_versao_py`).

## Cada proteção e o teste que falha sem ela

Cada uma foi desligada numa cópia à parte (git archive no rascunho da sessão, fora do projeto) e o teste dela falhou
(`anexos/reversao-resultado.txt`; o script em `anexos/reversao-mutacoes.py.txt`):
- Nada liberado antes da leitura de volta (recusa da ordem errada) →
  `tests/test_publicar_versao.py::test_d53_nada_e_liberado_antes_da_assinatura_lida_de_volta` (M1).
- Só os arquivos da versão vão ao destino, nunca o Setup.exe →
  `tests/test_publicar_versao.py::test_d768_o_motor_e_a_versao_publicados_numa_pasta_sem_o_motor_no_pacote` (M2).
- O rascunho do C: apagado e conferido também com erro (desfazer) →
  `tests/test_publicar_versao.py::test_d795_o_setup_exe_e_o_rascunho_somem_tambem_quando_da_erro` (M3).
- A conta do espaço recusa antes do vpk →
  `tests/test_publicar_versao.py::test_d776_sem_espaco_para_antes_do_vpk_e_nada_fica` (M4).
- A vigia fecha o vpk abaixo da reserva →
  `tests/test_publicar_versao.py::test_d776_a_vigia_fecha_o_vpk_quando_o_disco_cai_abaixo_da_reserva` (M5).
- A assinatura do motor publicado é conferida (leitura de volta) →
  `tests/test_publicar_versao.py::test_d724_o_motor_com_a_assinatura_de_outra_chave_e_recusado` (M6).
- O motor solto recusado no pacote da atualização →
  `tests/test_publicar_versao.py::test_d768_o_pacote_da_atualizacao_com_o_motor_solto_e_recusado` (M7).
- A falha antes de liberar apaga o rascunho do destino (desfazer) →
  `tests/test_publicar_versao.py::test_a_leitura_de_volta_que_nao_bate_nao_libera_e_apaga_o_rascunho_do_destino` (M8).
- Erro do GitHub nunca vira "não existe" →
  `tests/test_publicar_versao.py::test_o_github_sem_resposta_nunca_vira_nao_publicada` (M9).
- O servidor não serve o rascunho →
  `tests/test_publicar_servidor.py::test_d773_o_indice_junta_as_versoes_liberadas_e_nao_mostra_o_rascunho` (M10).
- A porta do servidor é exclusiva →
  `tests/test_publicar_servidor.py::test_a_porta_ocupada_vira_frase_e_a_janela_diz_que_nao_serve` (M11).
- A ficha confere o tamanho de cada arquivo →
  `tests/test_publicar_motor.py::test_o_motor_estragado_ou_de_outra_versao_nao_confere` (M12).
- O vpk sem a diferença →
  `tests/test_publicar_versao.py::test_d789_d777_o_comando_do_vpk_sem_diferenca_sem_portatil_e_o_msi_so_quando_pedido` (M13).
- O empacotar não abre o PowerShell por conta própria →
  `tests/test_windows_peca.py::test_o_empacotar_le_a_assinatura_pela_peca_e_nao_abre_o_powershell` (M14).
- A versão sem o motor publicado não é montada →
  `tests/test_publicar_versao.py::test_d790_sem_o_motor_publicado_nada_e_montado` (M15).
- A pasta pronta de outra versão é recusada →
  `tests/test_publicar_versao.py::test_a_pasta_pronta_de_outra_versao_e_recusada` (M16).
- O PowerShell sem a lista de módulos herdada →
  `tests/test_windows_peca.py::test_o_powershell_nao_herda_os_modulos_do_powershell_7` (M17).
- O script lançado solto apaga sem seguir atalho (D-809) →
  `tests/test_windows_peca.py::test_o_lancado_solto_apaga_a_pasta_de_troca_sem_seguir_atalho` (M18, no código anterior;
  acusa pelo JEITO de apagar: neste Windows o apagar antigo não entrou na junção, `anexos/d809-jeito-antigo.txt`).
- O destino não apaga uma publicação que é atalho (D-809) →
  `tests/test_publicar_versao.py::test_d809_apagar_uma_publicacao_que_e_atalho_nao_apaga_o_outro_lado` (M19).
- **Volta 2** (`anexos/reversao-volta2-resultado.txt`): o apagar do rascunho no GitHub sem a etiqueta (A1), a
  leitura de volta decide se apagou (A1b), o grupo fecha o que o vpk abriu (A2), nada apagado depois de liberar (A4), o
  erro do disco em frase (A5), o sinal de vida fora da pasta (A6), nome repetido não entregue (A7), o motor em
  instalar\ recusado na atualização (A8), a conta de 7 vezes (A9), a etiqueta inteira (A11), e N1, N3, N4, N5, N6,
  N8, N10, N13, N14: todas acusadas pelos testes citados no achado 3 e nos achados acima.
- Sem teste que acuse sozinho (dupla proteção; escrito para quem tenta quebrar): a conferência de que nada ficou vivo
  depois de fechar o grupo (A2b: o fechamento do Windows já fecha tudo; com ele desligado, o A2 acusa); o Ctrl+C que
  fecha o grupo (N10: o fechar-ao-fechar do grupo também cobre; com os dois desligados, acusa); o Setup.exe apagado logo depois do vpk
  (o rascunho inteiro some no fim de qualquer jeito); o corte das conexões no fechar do servidor (o envio também para
  pela marca de fechado).

- **Volta 3** (`anexos/reversao-volta3-resultado.txt`; script em `anexos/reversao-volta3-mutacoes.py.txt`), cada uma
  desligada numa cópia e acusada:
  - só o rascunho apagado (B1, B1b, B1c, B1d) →
    `tests/test_publicar_versao.py::test_volta3_achado1_uma_leitura_atrasada_depois_de_liberar_nunca_apaga_a_versao_liberada`
    e `tests/test_publicar_versao.py::test_volta3_achado1_no_github_a_leitura_atrasada_tambem_nunca_apaga_a_liberada`;
  - a cópia pelo nome provisório (B2) → `tests/test_publicar_versao.py::test_volta3_a_copia_cortada_no_meio_nunca_deixa_o_nome_certo`;
  - a cópia lida de volta (B2b) e a vigia no meio da cópia (B2e) →
    `tests/test_publicar_versao.py::test_volta3_a_copia_conferida_le_de_volta_e_obedece_a_vigia`;
  - a conferência do fim compara o .msi (B2c) →
    `tests/test_publicar_versao.py::test_volta3_achado2_o_msi_da_pasta_de_saida_e_comparado_com_o_do_rascunho`;
  - o .msi pela cópia conferida (B2d) →
    `tests/test_publicar_versao.py::test_volta3_achado2_o_msi_que_nao_termina_de_copiar_nao_fica_com_o_nome_certo`;
  - a peça recusa o que não é programa (B3), pelo começo do arquivo (B3b) →
    `tests/test_windows_peca.py::test_bat_e_cmd_sao_recusados_pelo_rodar_pelo_lancar_e_pelo_grupo`; pela extensão (B3c) →
    `tests/test_windows_peca.py::test_um_lote_que_a_peca_nao_acha_tambem_e_recusado_pela_extensao`;
  - o programa nasce parado (B4) → `tests/test_windows_peca.py::test_o_programa_nasce_parado_e_so_roda_dentro_do_grupo`;
  - "conferido" só fechando o grupo (B4b) e só com 0 vivos lidos (B4c), "não deu para conferir" sem leitura (B9) →
    `tests/test_windows_peca.py::test_fechar_tudo_so_diz_conferido_quando_o_windows_diz_que_nenhum_ficou` (B4b também por
    `tests/test_publicar_versao.py::test_volta3_achado4_a_vigia_fecha_o_filho_do_vpk_antes_de_soltar_o_grupo`);
  - a primeira pasta de troca apagada (B9b) →
    `tests/test_windows_peca.py::test_o_lancado_solto_apaga_a_primeira_pasta_se_a_segunda_nao_nasce`;
  - o rascunho apagado quando o liberar falha (B5) →
    `tests/test_publicar_versao.py::test_volta3_achado5_o_liberar_que_falha_e_continua_rascunho_apaga_o_rascunho`;
  - o motor que mudou (B6) → `tests/test_publicar_versao.py::test_volta3_achado6_o_motor_trocado_durante_a_publicacao_impede_liberar`;
  - o motor baixado na conta (B7) e na vigia (B7b) →
    `tests/test_publicar_versao.py::test_volta3_achado7_o_motor_baixado_entra_na_conta_e_na_vigia`; o gh na vigia (B7c) →
    `tests/test_publicar_versao.py::test_volta3_achado7_o_gh_que_baixa_e_fechado_pela_vigia`; o nome do motor num lugar
    só (B7d) → `tests/test_publicar_versao.py::test_volta3_achado7_o_nome_do_motor_so_em_versao_py`;
  - a janela diz do nome repetido (B8) →
    `tests/test_publicar_servidor.py::test_achado8_o_nome_repetido_aparece_na_janela_como_repetido_e_nao_como_inexistente`.
  - Sem teste que acuse sozinho (dupla proteção): a conferência IsProcessInJob depois de pôr no grupo (o
    AssignProcessToJobObject que deu certo já põe; sem ele, o B4 acusa). Na primeira passada, a B1d e a B2 não foram
    acusadas: a B1d porque o teste só cobrava "NÃO apaguei" (passou a cobrar "ficou liberada em"); a B2 porque o apagar
    do pedaço também a cobre na falha comum (ganhou o teste da cópia cortada no meio, sem nada rodando depois).

## De onde vem cada dado da conferência

- **Se a versão ou o motor já existem no destino:** lido do destino (a pasta; ou o GitHub pelo gh), nunca de uma
  anotação do publicar.
- **A soma de cada arquivo publicado:** lida do destino (a pasta: somada do arquivo lá; o GitHub: a soma que o próprio
  GitHub calcula, ou o arquivo baixado e somado), comparada com a soma do arquivo do rascunho.
- **A assinatura:** o texto baixado do destino, conferido com a chave pública que vai dentro do programa (nos testes, a
  chave de teste) e com a soma lida do destino. A chave privada não confere nada (ela assina).
- **O motor que a versão pede:** a assinatura do motor baixada do destino e a soma do arquivo do motor lida do destino;
  o motor-exigido.json é escrito a partir disso, nunca de um arquivo local.
- **O índice das versões:** baixado do destino, conferido contra a soma do pacote lida do destino.
- **O espaço livre:** lido do Windows na hora (`shutil.disk_usage`), a cada 2 s durante o vpk.
- **A versão da pasta pronta:** a ficha da versão dentro da pasta. **Este dado o conferido pode trocar** (quem monta a
  pasta escreve a ficha): ela pega o engano (a pasta de outra versão), não serve de prova; a prova é a leitura de volta
  do que foi publicado e a prova à vista.
- **O motor inteiro:** a ficha motor.json dentro do motor. **Também escrita por quem monta**: a conferência forte é a
  soma assinada do arquivo do motor, lida do destino.
- **O resultado do vpk:** os arquivos que ele deixa na pasta de saída, abertos e conferidos (o pacote aberto como zip),
  não só o código de saída dele.
- **O servidor:** as subpastas liberadas da pasta, lidas a cada pedido.

- **Volta 3:** o .msi feito agora: o nome, o tamanho e a soma lidos do arquivo no rascunho, logo depois de o vpk
  gravá-lo e antes de o rascunho ser apagado; o .msi da pasta de saída: lido do arquivo de lá (tamanho e soma). Quem
  escreve os dois é o próprio publicar; a prova de que o instalador está certo continua sendo a leitura de volta da
  publicação (a soma lida do destino) e a prova à vista.
- **Volta 3:** se o programa entrou no grupo: perguntado ao Windows (IsProcessInJob); quantos estão vivos no grupo:
  perguntado ao Windows (QueryInformationJobObject); se o arquivo é programa: o começo do arquivo lido do disco e o
  caminho completado pelo Windows (GetFullPathNameW, pelo os.path.abspath).
- **Volta 3:** só o rascunho apagado: a situação lida do destino dentro do apagar, antes e depois de pedir (na pasta,
  a subpasta do rascunho é a única tocada).

## Máquina ou olho

- Máquina: tudo o que está em "Testes" (a lógica, a pasta de verdade como destino, o servidor de verdade, a vigia com
  um processo de verdade, a assinatura digital lida pelo Windows de verdade).
- Olho: nada nesta entrega. A prova à vista (o vpk de verdade no C:, o rascunho no GitHub de verdade, a janela do
  servidor na tela) é da gerente com o Samuel, depois de quem tenta quebrar.

## Ressalvas

- **O vpk de verdade e o GitHub de verdade não rodaram.** Os testes usam um vpk de mentira (escreve os nomes que li no
  código do vpk) e um gh de mentira (responde no formato que li no código do gh). Pode dar diferente na prova: os nomes
  dos arquivos que o vpk 1.2.161 grava (conferidos só na pasta da etapa 5), o "digest" das publicações de rascunho do
  GitHub (se faltar, o publicar baixa o arquivo para somar: mais lento, ainda certo), e o gh achar o rascunho pela
  etiqueta.
- **A conta do espaço é conta, não medida** (volta 2, achado 9, refeita pela leitura do vpk: 4 vezes a pasta na
  atualização, 7 com o .msi, mais 1 GB; na volta 3, mais o motor baixado para o rascunho; fontes no docstring de
  `empacotar.espaco_que_vai_usar`). Corrigido na volta 3 (achado 8: as duas contas daqui se contradiziam). Pela pasta
  de hoje sem o motor (0,78 GB, medida por quem tentou quebrar) e o motor comprimido (uns 0,8 GB, conta, não medido):
  sem o .msi a conta dá uns 4,1 GB (o C: precisa de uns 24 GB livres); com o .msi, uns 13,7 GB (precisa de uns 34 GB
  livres). Hoje o C: tem 48,9 GB livres (medido por quem tentou quebrar). O .msi com o motor nunca foi medido; se a
  conta for alta demais, o publicar recusa com espaço que bastaria (é de propósito, pelo pior caso).
- **A pasta do programa ainda é montada no D:** (o PyInstaller, em dist\EditorImpressao\); no C: ficam o trabalho do
  vpk e o rascunho. Sem o motor, a pasta tem uns 582 arquivos e o vpk lê rápido do D: (estudo). Mudar também a pasta
  para o C: mexeria no Inno; não fiz.
- **O motor que existe hoje não tem a ficha.** Para publicar o motor 1, alguém roda uma vez
  `montar_motor_kraken.py --so-ficha --destino D:\programas\EditorImpressao-arquivos\ferramentas\motor-kraken`: abre o
  motor (1 minuto) e grava o motor.json **dentro da pasta de ferramentas do Samuel** (fora do projeto; não apaga nada).
  Não rodei: é coisa da gerente com o "sim" dele.
- **A pasta do publicar com `--pasta` mudou de desenho** (uma subpasta por versão, como o GitHub). O programa de hoje,
  pela fonte de teste da etapa 5, lê uma pasta plana: ele não acha as versões nesse desenho. Nas provas as versões vêm
  pelo servidor (D-773); o programa fala com o servidor no passo 3 (a fonte de teste aponta para o endereço). Até lá, o
  servidor só pode ser provado com um cliente comum (o teste faz isso).
- **A ficha da versão** (versao-do-pacote.json, a versão e o commit) passou a ir também na pasta portátil e no
  instalador do Inno: um arquivo pequeno a mais, sem efeito no programa.
- **Duas peças de conversa com o GitHub:** a do publicar (`DestinoGitHub._gh`) e a do porteiro
  (`regras_dos_agentes/conversa_com_o_github.py`, fora da lista dos meus arquivos). Fazem coisas diferentes (publicar e
  ler rodadas), mas o §11.12, ponto 1, pede uma peça só por conversa: fica para a gerente decidir se junta.
- **Os dois nomes para "onde achar o motor"** (para montar: `empacotar.LUGARES_DO_MOTOR`; onde o programa procura:
  `ocr_kraken.lugares_do_motor`) não foram trocados, porque testes antigos usam os nomes de hoje; ficaram escritos nos
  comentários das duas. O plano pedia nomes diferentes.
- **A versão do protocolo está escrita em dois lugares** (`core/ocr_kraken.py` e `montar_motor_kraken.py`), como antes;
  a ficha usa a do `core/ocr_kraken.py`. Não mexi na do montar (o teste do fim do montar confere as duas).
- **Achado do servidor (consertado):** o http.server deixava dois servidores na mesma porta no Windows (o segundo
  "servia" sem erro). Consertado com a porta exclusiva; o teste falha no jeito de fábrica (mutação M11).
- **A conversa com o GitHub não foi rodada contra o GitHub de verdade, nem como rascunho** (o pedido proíbe sem a
  gerente).
- **Depois de pedir para liberar, nada é apagado** (volta 2, achado 4, decisão técnica da gerente, D-014): se a
  leitura que vem depois falhar, o publicar lê a situação; só se ainda for rascunho, apaga. Se ficou liberada (ou não dá
  para ler), para com "liberada; não deu para reconferir agora" e "NÃO apaguei". **Por quê:** quando o liberar é pedido,
  tudo já foi lido de volta e conferido (a versão está inteira); apagá-la deixaria o número dela livre para outro
  conteúdo, e um programa que a pegou naqueles segundos nunca pegaria a outra, que teria o mesmo número ("um número de
  versão só", peça 8). Isso muda o "nunca pela metade" do plano só neste ponto: a versão inteira fica.
- **O conserto da lista de módulos mexe na peça do passo 1** (todo PowerShell que ela abre passa a nascer sem a lista
  herdada). Os testes do passo 1 continuam passando (`tests/test_windows_peca.py`, `tests/test_windows_janela_de_prova.py`).
  O que a peça faz com licença de administrador (a pergunta do Windows, as tarefas) não foi rodado de novo: a próxima
  prova à vista que usar a peça confere.
- O aviso K14 do formulário ("mexeu em arquivo fora da lista": a lista de exceções) é o item tirado da lista, que o
  pedido mandou.

- **Volta 3, o instante do GitHub:** no GitHub, o apagar do caminho de erro lê a situação logo antes de pedir; se o
  GitHub liberar entre essa leitura e o pedido (o liberar que se perdeu e chega atrasado), a versão liberada seria
  apagada, sem a etiqueta (o pedido de rascunho não leva `--cleanup-tag`). A API do GitHub não tem "apague só se for
  rascunho" (lembrado, não relido nesta volta). Na pasta das provas isso não acontece (só a subpasta do rascunho é
  tocada). O teste cobra a leitura atrasada, não esse instante.
- **Volta 3, a vigia no download do GitHub** olha a cada 2 s e fecha o gh; não foi rodada contra o gh de verdade (o
  teste usa um programa de prova que demoraria 60 s). Na pasta das provas, a vigia olha no começo e a cada 64 MB.
- **Volta 3, a peça abre o programa do grupo parado**, e quem o solta é a foto das linhas do Windows. Rodado no PC
  com o Python; o vpk de verdade não foi aberto assim (é da prova à vista). Se o Windows não deixar soltar, o programa
  é fechado e o publicar para com "não consegui soltar o programa depois de pô-lo no grupo".
- **Volta 3, a cópia conferida lê o arquivo duas vezes** (copia e lê de volta). No envio à pasta das provas (D:) e no
  .msi para a pasta de saída, isso soma alguns segundos por arquivo grande; não medi.
- **Volta 3, o achado 10 (para o passo 3; não é defeito hoje):** `windows.abrir_em_grupo` abre o programa com o console
  de quem chama. Do publicar (um terminal), está certo: a saída do vpk aparece ali. Se o programa do Kaique (que não
  tem console) chamasse o grupo para um programa de console, o Windows abriria uma janela preta nova na tela dele.
  Como evitar sem mexer em mais nada: quando quem chama não tem console, abrir com a bandeira CREATE_NO_WINDOW
  (Microsoft Learn: "The process is a console application that is being run without a console window"; o porteiro só
  barra a bandeira de processo sem console, DETACHED_PROCESS, não esta) e mandar a saída para um arquivo; a decisão de
  quando (um parâmetro de quem chama, ou perguntar ao Windows se há console) fica para o pedido do passo 3. Não mudei.
- **Volta 3, o comentário da peça:** a primeira versão do comentário da recusa do lote citava de memória a correção do
  Rust (BatBadBut); relida a página do Rust, ela não diz isso, e o comentário passou a dizer o que foi rodado no PC
  (`e4263c0a`).
- **Volta 3, uma pasta fora do projeto:** num ensaio rápido criei `C:\Users\fotog\AppData\Local\Temp\tmpqhb16hsh`
  (três .bat e um .exe de lote, de poucos bytes) fora da pasta de rascunho desta conversa. Não apaguei (regra de
  29/09): a gerente decide.

## Velocidade

Não se aplica: nenhum arquivo do processamento das páginas do livro mudou; em `core/ocr_kraken.py` só
entraram a versão do motor, a ficha e a conferência, que o caminho do livro não chama (a segunda opinião do Kraken está
desligada, D-164). A gerente decide se roda o filtro de velocidade do GitHub (D-786; plano-v3, "Regras de todos os
passos"). O tempo de publicar é medido na prova à vista.

## Ideias e bugs

- Ideia (Lista de espera): juntar as duas peças de conversa com o GitHub (a do publicar e a do porteiro) numa só.
- Ideia (Lista de espera): um comando `--so-o-instalador` que faça o .msi da versão já publicada, sem publicar de novo
  (hoje o .msi sai junto com uma versão nova).
- Ideia (Lista de espera): a versão do protocolo do motor num lugar só (hoje está em `core/ocr_kraken.py`, em
  `montar_motor_kraken.py` e no servidor do motor).
- (Consertado na volta 2, pedido da gerente, achado 6): o lançar solto que dava "saiu sem começar" para um script
  curto. Já não vai para a Lista de bugs.
- Bug (Lista de bugs, 19/11/2026, não impede): o http.server do Python, de fábrica, deixa dois servidores abrirem a mesma
  porta no Windows; outros lugares do projeto que usem o http.server podem ter o mesmo defeito (não procurei fora deste
  passo).

- Bug (Lista de bugs, 20/11/2026, não impede): `DestinoGitHub.soma`, quando o GitHub não dá a soma de um arquivo,
  baixa o arquivo inteiro para a pasta temporária da conta (`%TEMP%`, no C:), fora do rascunho: fora da conta do espaço
  e da vigia (o pacote tem uns 460 MB). Achado lendo o código na volta 3; não é dos achados do relatório 2.
- Ideia (Lista de espera): a cópia do motor para instalar\ (`empacotar.preparar_saida`) pela cópia conferida também.

## Perguntas para o Samuel

Nenhuma nesta entrega. Procurei no Livro antes: a D-773, a D-776, a D-777, a D-788, a D-789, a D-790 e a D-795 respondem
tudo o que este passo precisou. O que depende de um "sim" dele é uma licença, não uma escolha (gravar a ficha na pasta
de ferramentas dele, em "Ressalvas"): a gerente pergunta, se achar preciso.

## Commit

e4263c0a (o último commit de código, volta 3; depois dele só este formulário e os anexos mudam).

## O que o agente que tentou quebrar achou

**Volta 1** (`quem-quebrou/relatorio-1.md`, commit `a58f181b`). Destino de cada achado (volta 2 deste agente; código em
`17cd8635` e `85781a08`; reversão em `anexos/reversao-volta2-resultado.txt`):
1. **O apagar de um rascunho no GitHub dizia "não deixou apagar" tendo apagado:** consertado. Lido o `delete.go` do gh
   (apaga a publicação e depois a etiqueta, que num rascunho não existe, e sai com esse erro): rascunho sem
   `--cleanup-tag`, liberada com; quem decide é a leitura de volta. O gh de mentira imita o de verdade, com a fonte.
   Testes: `tests/test_publicar_versao.py::test_achado1_apagar_um_rascunho_no_github_le_de_volta_e_nao_acusa_erro_falso`,
   `tests/test_publicar_versao.py::test_achado1_erro_antes_de_liberar_no_github_apaga_e_diz_que_apagou` e
   `tests/test_publicar_versao.py::test_achado1_quem_decide_se_apagou_e_a_leitura_de_volta`.
2. **A vigia fechava só o vpk:** consertado na peça do Windows, num lugar só (`windows.abrir_em_grupo`, um grupo do
   Windows que fecha tudo junto e confere que nada ficou vivo); `empacotar.rodar_vpk` o usa. Testes de verdade, num
   processo que abre outro: `tests/test_windows_peca.py::test_fechar_o_programa_em_grupo_fecha_tambem_o_que_ele_abriu` e
   `tests/test_publicar_versao.py::test_achado2_a_vigia_fecha_o_vpk_e_o_que_ele_abriu`.
3. **Nove proteções sem teste:** cada uma ganhou o seu (N1, N3, N4, N14:
   `tests/test_publicar_versao.py::test_n1_n3_n4_n14_cada_leitura_de_volta_errada_impede_liberar`; N5:
   `tests/test_publicar_versao.py::test_n5_o_apagar_que_nao_apaga_e_acusado`; N6:
   `tests/test_publicar_versao.py::test_n6_a_conferencia_do_fim_acusa_o_setup_exe`; N8:
   `tests/test_publicar_versao.py::test_n8_o_msi_nao_fica_na_pasta_de_saida_se_a_versao_nao_saiu`; N10:
   `tests/test_publicar_versao.py::test_n10_ctrl_c_fecha_o_vpk_e_o_que_ele_abriu`; N13:
   `tests/test_publicar_servidor.py::test_n13_o_servidor_nao_serve_por_uma_juncao`). Todos acusam com a proteção
   desligada; o N10 só com o fechar-ao-fechar do grupo desligado junto (é dupla proteção agora). Corrigida a afirmação de
   que o `test_d53` provava o N4.
4. **Apagar uma versão já liberada quando a leitura depois falha:** decisão técnica da gerente (D-014): não apaga; diz
   "liberada; não deu para reconferir agora". Porquê em "Ressalvas". Teste:
   `tests/test_publicar_versao.py::test_achado4_depois_de_liberar_a_leitura_que_falha_nao_apaga_a_versao`.
5. **Erro do disco cru:** consertado (frase em português). Teste: `tests/test_publicar_versao.py::test_achado5_erro_do_disco_vira_frase`.
6. **O lançar solto "saiu sem começar":** consertado (o sinal de vida numa pasta à parte). Teste repetido 20 vezes:
   `tests/test_windows_peca.py::test_o_lancado_solto_curto_nunca_vira_saiu_sem_comecar` (no código anterior: 12 de 20).
7. **O .msi de outra versão:** consertado (o .msi publicado com o número da versão; o servidor usa a regra única das
   publicações, `DestinoPasta.liberadas`, sem junção, e não entrega nome repetido). Teste:
   `tests/test_publicar_servidor.py::test_achado7_nome_repetido_em_duas_versoes_nao_e_entregue`.
8. **O motor em `instalar\` aceito na atualização:** consertado (lido de `SAIDAS`). Teste:
   `tests/test_publicar_versao.py::test_achado8_o_arquivo_do_motor_em_instalar_e_recusado_na_atualizacao`.
9. **A conta com o .msi curta:** refeita pela leitura do vpk (fontes no docstring de `empacotar.espaco_que_vai_usar`):
   4 vezes a pasta, 7 com o .msi. Teste: `tests/test_publicar_versao.py::test_d776_a_conta_do_espaco_e_a_reserva_de_20_gb`.
10. **A reversão da D-809 só pelo texto:** rodado de verdade o jeito antigo numa junção temporária
    (`anexos/d809-jeito-antigo.txt`): neste Windows ele não entrou na junção. A seção "Cada proteção" passa a dizer que
    o M18 acusa pelo jeito de apagar, não por arquivo perdido.
11. **A etiqueta com quebra de linha:** consertado (conferida inteira). Teste:
    `tests/test_publicar_versao.py::test_achado11_etiqueta_com_quebra_de_linha_e_recusada`.

**Volta 3** (`quem-quebrou/relatorio-2.md`, commit `9cd555a5`; agente novo, D-815). Destino de cada achado:
1. **Versão liberada apagada por uma leitura atrasada:** consertado pela causa (só o rascunho é apagado, lido de novo
   dentro do apagar). Testes: `tests/test_publicar_versao.py::test_volta3_achado1_uma_leitura_atrasada_depois_de_liberar_nunca_apaga_a_versao_liberada`
   (o caso do relatório: o liberar muda a pasta e devolve erro) e
   `tests/test_publicar_versao.py::test_volta3_achado1_no_github_a_leitura_atrasada_tambem_nunca_apaga_a_liberada`.
   Fica o instante do GitHub (Ressalvas).
2. **O .msi pela metade com o nome certo:** consertado (a cópia conferida; a frase diz que a versão foi publicada; a
   conferência do fim compara o .msi). Testes: `tests/test_publicar_versao.py::test_volta3_achado2_o_msi_que_nao_termina_de_copiar_nao_fica_com_o_nome_certo`,
   `tests/test_publicar_versao.py::test_volta3_achado2_o_msi_da_pasta_de_saida_e_comparado_com_o_do_rascunho`,
   `tests/test_publicar_versao.py::test_volta3_achado2_a_frase_do_fim_nao_diz_apagado_sem_conferir`,
   `tests/test_publicar_versao.py::test_volta3_a_copia_conferida_le_de_volta_e_obedece_a_vigia` e
   `tests/test_publicar_versao.py::test_volta3_a_copia_cortada_no_meio_nunca_deixa_o_nome_certo`.
3. **O .bat e o .cmd pela peça:** consertado na peça do passo 1 (regra única do rodar, do lançar e do grupo). Testes:
   `tests/test_windows_peca.py::test_bat_e_cmd_sao_recusados_pelo_rodar_pelo_lancar_e_pelo_grupo` e
   `tests/test_windows_peca.py::test_um_lote_que_a_peca_nao_acha_tambem_e_recusado_pela_extensao`. O vpk de mentira
   virou um programa de prova de verdade.
4. **O "conferido" do `fechar_tudo` e o instante do grupo:** consertado (nasce parado, entra no grupo, conferido, solto).
   Testes: `tests/test_windows_peca.py::test_o_programa_nasce_parado_e_so_roda_dentro_do_grupo`,
   `tests/test_windows_peca.py::test_fechar_tudo_so_diz_conferido_quando_o_windows_diz_que_nenhum_ficou` e
   `tests/test_publicar_versao.py::test_volta3_achado4_a_vigia_fecha_o_filho_do_vpk_antes_de_soltar_o_grupo` (fechar só
   o vpk não passa).
5. **O rascunho apagado quando o liberar falha:** teste novo,
   `tests/test_publicar_versao.py::test_volta3_achado5_o_liberar_que_falha_e_continua_rascunho_apaga_o_rascunho`.
6. **O motor que muda durante a publicação:** teste novo,
   `tests/test_publicar_versao.py::test_volta3_achado6_o_motor_trocado_durante_a_publicacao_impede_liberar`.
7. **O motor baixado fora da conta e da vigia; o nome escrito à mão:** consertado (a conta, a vigia única, o nome em
   `versao.py`). Testes: `tests/test_publicar_versao.py::test_volta3_achado7_o_motor_baixado_entra_na_conta_e_na_vigia`,
   `tests/test_publicar_versao.py::test_volta3_achado7_o_gh_que_baixa_e_fechado_pela_vigia` e
   `tests/test_publicar_versao.py::test_volta3_achado7_o_nome_do_motor_so_em_versao_py`.
8. **Textos que não batiam:** consertados (o cabeçalho da peça, o rascunho da pasta, a janela do servidor, a conta das
   Ressalvas). Teste da janela:
   `tests/test_publicar_servidor.py::test_achado8_o_nome_repetido_aparece_na_janela_como_repetido_e_nao_como_inexistente`.
9. **Sem a leitura do grupo, "continua rodando":** consertado ("não deu para conferir"); e a primeira pasta de troca
   apagada quando a segunda não nasce. Testes: `tests/test_windows_peca.py::test_fechar_tudo_so_diz_conferido_quando_o_windows_diz_que_nenhum_ficou`
   e `tests/test_windows_peca.py::test_o_lancado_solto_apaga_a_primeira_pasta_se_a_segunda_nao_nasce`.
10. **O console do grupo chamado pelo programa do Kaique:** anotado para o passo 3 (Ressalvas), com o jeito de evitar
    (CREATE_NO_WINDOW quando quem chama não tem console). Não mudei.

## A prova de verdade

Roteiro para a gerente (não rodado; D-785, item 8; o plano: "0 perguntas do Windows"; o Samuel olha a janela, não
clica nada):
1. Gravar a ficha do motor de hoje (com o "sim" dele, ver "Ressalvas"):
   `.venv\Scripts\python.exe montar_motor_kraken.py --so-ficha --destino D:\programas\EditorImpressao-arquivos\ferramentas\motor-kraken`.
2. Abrir o servidor das versões à vista: `.venv\Scripts\python.exe servidor_das_versoes.py --pasta <pasta de prova>`.
3. Publicar o motor 1 na pasta: `publicar_versao_kaique.py --motor --pasta <pasta de prova>`.
4. Publicar uma versão de prova no C: sem o .msi, com a janela do servidor mostrando a versão chegar: o espaço do C:
   antes e depois (volta ao que era), o tempo, e no fim a conferência mostra que o Setup.exe não está em lugar nenhum.
5. Um erro de propósito no meio (fechar o vpk pelo Gerenciador de Tarefas, ou desligar a internet antes do envio ao
   GitHub; olhar no Gerenciador de Tarefas que não sobrou cmd.exe nem wix.exe depois, achado 2; e que a frase do
   apagar no GitHub diz "foi apagada (conferido)", achado 1): o rascunho e o Setup.exe também somem. Na passada com o
   .msi, olhar também que o .msi da pasta de saída tem o tamanho do feito no rascunho (a linha "igual ao feito agora"
   da conferência do fim; relatório 2, "O que falta", item 4).
6. Outra versão com `--com-instalador`: medir o .msi com o motor num arquivo só.
7. O aviso de pouco espaço: com a reserva aumentada só nesta prova (`--reserva-gb` com um número maior que o espaço
   livre do C:; a opção só aumenta, nunca abaixo de 20 GB), o publicar recusa antes do vpk; o C: nunca é enchido.
8. No GitHub, como rascunho: `publicar_versao_kaique.py --motor` e a versão de teste sem `--pasta`; ler de volta,
   liberar, e no fim `--apagar v<versão>` e `--apagar motor-kraken-1` (conferido: "não existe").
9. Depois, as versões de prova do passo 3 (lista do plano): a primeira com o .msi (motor 1); uma boa; uma que nem abre;
   uma com a assinatura de uma chave falsa; uma que pede o motor 2, com o motor 2 verdadeiro e o motor 2 com assinatura
   falsa (o motor 2 pede aumentar `core/ocr_kraken.VERSAO_DO_MOTOR` numa cópia); e uma boa para o atualizar de longe.

## Perguntas do Windows que o Samuel vê

- Nesta entrega: 0 (nada pede licença; o publicar não pede).
- Na prova à vista: 0 (o plano: "0 perguntas do Windows"). O servidor escuta só em 127.0.0.1: o firewall não pergunta.

## Páginas em que foi conferido

Não se aplica: nenhuma página de livro passa por este passo (0 páginas). Os arquivos com a etiqueta de imagem
(`montar_motor_kraken.py`, `core/ocr_kraken.py`) mudaram só na ficha e na conferência do motor, que não tocam a imagem
de nenhuma página.
