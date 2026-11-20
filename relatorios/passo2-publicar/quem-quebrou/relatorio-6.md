# Passo 2 do plano da parte do Windows: sexta conferência de quem tentou quebrar (20/11/2026)

Sou um agente novo nesta volta (D-815). Não escrevi este código e não fiz as voltas anteriores. Não mexi no código do
outro.

O que **não** fiz:

- não rodei o publicar, o PyInstaller, o vpk nem o `gh release` de verdade (D-785, item 8);
- não pedi licença de administrador e não abri janela na tela do Samuel;
- não disparei rodada do GitHub (só consultei a 44800950547);
- não mexi em `C:\EditorImpressaoProva` nem na pasta `dist\EditorImpressao` da prova (só li).

Tudo rodou em cópias do código (`git archive` de `b9300da8` e de `3abf9acf`), na pasta de rascunho desta conversa, um
arquivo de teste por vez.

## Pedido

- Papel: quebrador
- Commit de partida: 73e36716
- Ramo: passo2-publicar-2026-11-19

## Arquivos que vou mexer

- `publicar_versao_kaique.py`
- `empacotar.py`
- `core/windows.py`
- `tests/test_windows_peca.py`
- `tests/test_empacotar.py`
- `tests/test_publicar_*.py`
- `relatorios/passo2-publicar/`

(Copiado do pacote sem mudar. Na prática só escrevi em `relatorios/passo2-publicar/quem-quebrou/`: este relatório, nos
três formatos, e a pasta `anexos-6/`. O pacote `anexos/pacote-quem-quebra-volta6.md`, que a gerente gerou, vai no mesmo
commit, como ela pediu.)

## Veredito

**NÃO ESTÁ PRONTO: o defeito da prova está consertado pela causa, mas a conferência da pasta que vem de fora ainda
deixa passar uma pasta errada até o Kaique.**

O que está certo:

- **O defeito da prova de 20/11 está consertado pela causa.** A montagem do zero agora põe o Visual C++ antes da ficha.
  A mesma conferência roda para os dois caminhos, e de novo antes do vpk. Rodei os testes novos no código antigo: 7 de 8
  falham, como o outro escreveu. No código novo, todos passam.
- **Os 3 baixos do relatório 5 estão consertados.** A frase do motor dá o comando com o `--pasta`, e segui-la publica na
  pasta. O caminho de rede tem a frase própria. O apagar em que o gh nem abre ganhou teste.
- **Nada do que funcionava em volta quebrou.** 11 arquivos de teste, um por vez, todos passam. A rodada do GitHub
  44800950547 passou na primeira tentativa, sobre o código desta volta.

O que impede (achado 1, médio): a pasta pronta (`--pasta-pronta`) é conferida bem menos que a montada. Uma pasta sem o
Tesseract e com um "Visual C++" qualquer, sem a versão dele ao lado, passa em todas as conferências e é publicada. No
notebook do Kaique, esse arquivo é rodado pela tarefa do Windows como SYSTEM, e com o Visual C++ velho instalado o
programa nem tenta trocar. A tentação existe agora: a pasta da prova de 20/11 "só falta o Visual C++", e copiar o
arquivo à mão para dentro dela passaria.

Mais 4 baixos (um deles no roteiro da prova: o item 14 não dá para fazer depois do 13) e 5 observações. Desliguei 11
proteções minhas, diferentes das 10 do outro: os testes acusaram 7.

Pela D-775, a gerente decide se volta para quem escreveu antes da prova à vista. Se seguir para a prova sem consertar o
achado 1, o roteiro precisa da troca do achado 2 e de nunca usar `--pasta-pronta` numa pasta arrumada à mão. Nunca
"aprovado": só o Samuel aprova.

## Decisões que esta tarefa precisa cumprir

- D-727 "pode, se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador né". Aqui: **pela
  metade**. Montada do zero: o Visual C++ e a versão dele vão no pacote (o teste novo confere os dois, com e sem o
  instalador). Pela pasta pronta: só se cobra que exista um arquivo com o nome `vc_redist.x64.exe`, e o Tesseract nem
  é procurado (achado 1).
- D-767 "não faça mais nada escodindo ou de mentira". Aqui: **cumprida no que o teste novo mostra**. O PyInstaller de
  mentira do teste não é mais pronto que o de verdade em nada do que se confere (comparei com a pasta da prova, abaixo).
  Ao contrário: a pasta de mentira antiga (`_pasta_pronta`) é menos completa que a de verdade e passa justamente porque
  a conferência é fraca (achado 1). O vpk de verdade continua só na prova à vista.
- D-773 "A". Aqui: **cumprida**. Na pasta das provas, a frase do motor que falta diz
  `publicar_versao_kaique.py --motor --pasta "<pasta>"`, e o teste segue a frase e confere que nada vai ao GitHub. As
  aspas do caminho não têm teste (achado 5).
- D-775 "ok". Aqui: tentei quebrar, sem pergunta do Windows. O resultado vai à gerente.
- D-776 "Sim, no C só tem que cuidar para não encher o disco C inteiro". Aqui: nada desta volta toca a conta do espaço
  nem a vigia (conferido no diff). O Visual C++ (uns 25 MB) entra no tamanho da pasta, que a conta já mede do disco.
- D-777 "ok, fica assim". Aqui: nada mudou no .msi (conferido no diff); o teste novo cobra o .msi só com o instalador.
- D-785 (item 8, publicar sempre à vista). Aqui: não rodei o publicar de verdade.
- D-788 "1" e D-789 "A". Aqui: o teste novo cobra que o pacote montado do zero sai sem o motor solto; nada mudou no
  motor publicado.
- D-795 "ok". Aqui: nada mudou no Setup.exe; o teste novo confere que nenhum rascunho sobra.
- D-815 "ok". Aqui: sou um agente novo nesta volta, sem memória da anterior.
- D-816 "A , mas onde estamos antes de você fazer qualquer processo" e D-817 "pode". Aqui: nada desta volta toca o
  liberar nem o apagar depois do pedido; os `test_d816_*` passam no arquivo inteiro (85 de 85).

## O que li

- `.claude/agents/verificador.md` e o `CLAUDE.md` inteiro (na cópia `passo2`; difere da do projeto só na parte da
  Central), com atenção ao §4.7, §11.8, §11.12 (os 6 pontos) e §11.13.
- `memoria/INDICE.md` (na cópia `passo2`), `memoria/geral/atualizador.md` (só existe na pasta do projeto,
  `D:\programas\EditorImpressao\memoria\geral\atualizador.md`; na cópia `passo2` não há) e o catálogo dos erros
  (`obra-juncao`, famílias F1 a F10).
- O meu pacote (`anexos/pacote-quem-quebra-volta6.md`). Ele diz "D-815 a D-817: NÃO ACHADA NO LIVRO"; achei as três no
  Livro da `obra-juncao` (linhas 1105 a 1107) e li inteiras, com as outras 10 pedidas.
- No ONDE-PAREI do escritor, todas as partes "Volta 6": "Onde parei", decisões, "O que já está escolhido", "A causa, a
  regra e todos os caminhos" (a tabela dos 10 caminhos), "O que pode falhar", "O que li", "O que foi feito", "Testes",
  "Caminho e função", "Cada proteção", "De onde vem cada dado", "Ressalvas", "Ideias e bugs", "O que o agente que tentou
  quebrar achou" e "A prova de verdade" (itens 1 a 15).
- O relatório 5 de quem tentou quebrar e os anexos `reversao-volta6-*` e `volta6-a-pasta-da-prova.txt`.
- O código: `git diff b9300da8 3abf9acf` inteiro. Li inteiras, no código novo: `construir_pasta`,
  `preparar_pasta_para_o_velopack`, `preparar_saida`, `construir_pacote_do_velopack`, `conferir_pasta_pronta`,
  `esperados_no_pacote_do_velopack`, `conferir_pacote_do_velopack`, `gravar_ficha_da_versao`, `preparar_vc_redist`,
  `vc_redist_confere`, `comando_do_pyinstaller` (empacotar); `publicar`, `obter_motor_publicado`, `_Destino` e
  `DestinoPasta` (os comandos), `_pedir_para_apagar`, `main` (publicar); `_caminho_do_programa` e `_por_que_recusa`
  (peça do Windows); `instalar_visual_c_se_faltar` e `preparar_o_computador` (atualizacao). E os testes novos inteiros.
- O registro da prova (`C:\EditorImpressaoProva\publicar-versao.log` e `publicar-motor.log`, UTF-16) e a pasta
  `dist\EditorImpressao` da cópia `passo2` (797 MB), só lidos.
- Peça de fora: nesta volta nada novo. A única é `shutil.copy2` (biblioteca do Python): copia o conteúdo e a data; se o
  disco enche no meio, levanta `OSError` e deixa o arquivo pela metade (documentação do Python, `shutil`). Conferi esse
  caso rodando (sonda S4, abaixo).

## O que conferi nas falhas, nas peças de fora e nos caminhos

### O defeito da prova: a causa e a prova de reversão (anexo `reversao-testes-novos-no-codigo-antigo.txt`)

- No registro da prova (lido): a montagem disse "pronto: ...\dist\EditorImpressao (797 MB)" e logo depois
  "PAREI: a pasta do programa não serve: ... não tem o Visual C++ em instalar\". Bate com a causa que o outro escreveu.
- Na pasta da prova (lida): `.exe`, `_internal`, `tesseract`, a ficha (versão 1.1.0, saída "atualização", commit
  `b9300da8`) e nenhuma `instalar\`. A conferência do código novo, rodada sobre ela, ainda recusa ("não tem o Visual
  C++"), como o item 14 do roteiro espera.
- Os testes novos no código de `b9300da8` (cópia minha, com os dois arquivos de teste de `3abf9acf` por cima): **7 de 8
  falham**, como o outro escreveu. Os dois do defeito falham com a frase da prova. O do achado 1 passa (a proteção já
  existia). Ressalva pequena: o caso `[github]` do achado 2 falha no código antigo só porque a função nova não existia
  (`AttributeError`); no GitHub o comando antigo já estava certo. Ele prova "o mesmo resultado nos dois destinos", não um
  defeito.
- No código novo: `test_publicar_versao.py` 85 passaram; `test_windows_peca.py` 69 passaram e 2 pulados.

### O PyInstaller de mentira contra a pasta de verdade (D-767)

| | PyInstaller de mentira do teste | A pasta de verdade da prova (só lida) |
|---|---|---|
| o `.exe` | um arquivo que começa com "MZ" | `EditorImpressao.exe`, 21,9 MB |
| `_internal` | só o que os `--add-data` mandam (recursos, modelos, a DLL) | isso e mais o Python inteiro (29 pastas) |
| `tesseract`, a ficha, `COMO USAR.txt` | postos pelo `construir_pasta` de verdade | os mesmos, postos pelo mesmo código |
| `instalar\` | posto pelo `construir_pasta` de verdade (volta 6) | não tem (código antigo) |

Nada do que as conferências cobram (o `.exe`, os modelos, a DLL, o Tesseract, o Visual C++, a ficha, nenhum
`motor-kraken\`) existe na de mentira sem existir na de verdade. **O teste novo não passa por usar algo mais pronto que
o de verdade.** O que a de mentira não tem (o Python) nenhuma conferência olha. Lido na fonte e na pasta.

### Os caminhos até o vpk (a tabela do outro, conferida um por um)

| Caminho | Passa pela mesma conferência antes do vpk? | Chega com a pasta certa? |
|---|---|---|
| publicar montado do zero | sim, duas vezes (cedo e antes do vpk) | sim: a montagem confere o Visual C++ pela assinatura e pelo tamanho |
| publicar `--pasta-pronta` | sim | **não sempre:** só se cobra o nome do arquivo do Visual C++; o Tesseract e a versão do Visual C++ não (achado 1) |
| a segunda passada do instalador | sim (`conferir_pasta_pronta(INSTALADOR)`, depois de pôr o motor) | sim, a mesma pasta da primeira |
| a volta da pasta depois do instalador | não vai ao vpk; tira o zip do motor, também com erro (`finally`) | sim |
| `construir_pacote_do_velopack` chamado sozinho | sim, mas **depois** de `preparar_saida` mexer na pasta (achado 4) | a pasta recusada já foi mudada |
| a pasta portátil e o Inno | não vai ao vpk; sem `instalar\` (o teste cobra) | sim |
| a conferência do pacote depois do vpk | lê o mesmo campo `vc_em_instalar` | a parte do Visual C++ não tem teste (achado 3) |

### A cópia do Visual C++ que falha no meio, e a pasta de antes do conserto (sondas, anexo `sondas6-*`)

- **Cópia cortada** (teste do outro) e **disco cheio no meio** (minha sonda S4: a cópia escreve 5 bytes e levanta
  "Não há espaço suficiente no disco"): a montagem para, a ficha não é gravada, o rascunho do C: é apagado, o vpk não
  roda, e a frase diz "PAREI: o disco não deixou terminar (...\instalar\vc_redist.x64.exe)". A pasta pela metade fica em
  `dist\`, e um `--pasta-pronta` nela é recusado ("não tem a ficha da versão: monte de novo"). **Nada passa como pronto.**
- **A pasta de antes do conserto:** a da prova de 20/11 é recusada (rodado). Mas se alguém copiar à mão um
  `vc_redist.x64.exe` para dentro dela, ela passa: a ficha diz o commit `b9300da8`, e ninguém lê o commit (sonda S2).
  Junto com o achado 1.

### Um lugar só (§11.12)

- **Pôr o Visual C++:** só `preparar_pasta_para_o_velopack`, chamada só pela montagem (grep em todo o projeto fora de
  `tests`, `dist`, `build`). O Inno copia o seu para `build\` em outro lugar (`construir_instalador`), outro instalador,
  de antes; não é deste trabalho.
- **"A saída leva o Visual C++?":** o campo `Saida.vc_em_instalar`, lido nos três lugares (montagem, conferência da
  pasta, conferência do pacote). Sem desvio para um caso.
- **"O Visual C++ é o oficial?":** aqui há **duas réguas** para a mesma regra. A montagem confere pela assinatura da
  Microsoft (`vc_redist_confere`) e pelo tamanho; a pasta pronta, só pelo nome do arquivo (achado 1).
- **Os comandos das frases:** `comando_de_apagar` e `comando_de_publicar_o_motor`, pelos mesmos
  `_argumentos_do_destino`. Procurei `--motor`, `--apagar` e `.py --` nas frases do publicar e do empacotar: fora o
  cabeçalho e o `main`, nenhum comando do destino escrito à mão.
- **A frase do caminho de rede:** sai da regra única `_por_que_recusa`, pelos três caminhos da peça.

### As mutações minhas (anexo `mutacoes6-resultado.txt`; script `mutar_quebra6.py.txt`)

Numa cópia de `3abf9acf`, uma por vez, o arquivo devolvido ao original depois de cada uma (conferido byte a byte). Rodei
o arquivo de teste inteiro, não só os testes novos.

| | O que desliguei | Acusada? |
|---|---|---|
| Z1 | a montagem não grava a versão do Visual C++ ao lado dele | sim (2 testes novos) |
| Z2 | a conferência do pacote depois do vpk deixa de procurar o Visual C++ | **não** (85 + 41 passam) |
| Z3 | o publicar deixa de conferir a pasta cedo | sim (um teste antigo) |
| Z4 | o publicar montado do zero passa `pecas=None` (o pacote não é conferido no Tesseract) | **não** |
| Z5 | o pedido de apagar trata qualquer erro do gh como "pedi" (outra rota do achado 1) | sim |
| Z6 | o comando da pasta sem as aspas no caminho | **não** |
| Z7 | a conferência só olha se a pasta `instalar\` existe | sim |
| Z8 | `preparar_saida` volta a pôr o Visual C++ (dois lugares) | **não** (85 + 12 + 41 passam) |
| Z9 | a montagem põe o Visual C++ só na saída com .msi | sim (4 testes novos) |
| Z10 | a conferência antes do vpk confere como pasta portátil | sim |
| Z11 | o caminho de rede com a frase do "não consegui ler" | sim (3 testes) |

**7 de 11 acusadas.** As 4 que passam estão nos achados 3, 5 e na observação 1.

### O que já funcionava em volta (§11.8; anexo `arredor-um-arquivo-por-vez.txt`)

Código de `3abf9acf`, um arquivo por vez: `test_publicar_versao.py` 85; `test_empacotar.py` 41;
`test_publicar_motor.py` 12; `test_windows_peca.py` 69 e 2 pulados; `test_publicar_servidor.py` 14;
`test_windows_janela_de_prova.py` 10; `test_decisoes_atualizacao.py` 38; `test_decisoes_ajudante_da_atualizacao.py`
37; `test_decisoes_testes_a_distancia.py` 13; `test_decisoes_brasao.py` 22; `test_nome_do_pacote.py` 5. Todos passam,
e bate com o que o outro escreveu. Nenhum teste antigo mudou nesta volta (o diff dos testes só acrescenta).

### A rodada do GitHub 44800950547 (anexo `rodada-44800950547-o-que-foi-testado.txt`)

Consultei uma vez: tentativa 1, success, todas as partes, os botões, o porteiro e o resumo. O registro diz "código
trocado pelo de passo2-publicar-2026-11-19 (d73e7fc8...)". De `3abf9acf` a `d73e7fc8` nenhum `.py` mudou (conferido
no `git diff`). Então o código testado é o desta volta.

## Caminhos que o outro não listou

1. **A pasta pronta "arrumada à mão"** (a da prova de 20/11 com o Visual C++ copiado para dentro): passa pela
   conferência, com o código antigo dentro e sem a versão do Visual C++ (achado 1 e sonda S2).
2. **O item 14 do roteiro depois do item 13:** a pasta de 20/11 é a mesma `dist\EditorImpressao` que o item 13 apaga e
   monta de novo (achado 2).
3. **A pasta recusada pelo empacotar chamado sozinho é mudada antes da recusa** (achado 4).
4. **A conferência do pacote depois do vpk sem o Visual C++** (achado 3): o outro a chama de "a prova forte".

## Falhas não pensadas e resultado não conferido

- **Dá como pronto o que não conferiu (F5) e a conferência que acredita num dado fraco (F1):** a pasta pronta passa com
  um "Visual C++" que ninguém conferiu, sem o Tesseract e sem a versão (achado 1). O dado que decide é só "existe um
  arquivo com esse nome".
- **Proteção sem teste (F3):** a parte do Visual C++ da conferência do pacote (Z2, achado 3); o Tesseract no pacote
  montado do zero (Z4, achado 3); as aspas do comando (Z6, achado 5); o "lugar único" do Visual C++ (Z8, observação 1).
- **Mexer antes de conferir:** a pasta recusada já mudou (achado 4).
- **O escrito não bate (F7):** o roteiro da prova pede uma coisa que não dá para fazer naquela ordem (achado 2); "agora
  o teste novo percorre o Tesseract" é verdade, mas o teste não acusa se a conferência dele sumir (achado 3).
- **F9 (mexer no que é do Samuel sem ele ver):** nada. Não criei junção. `git rev-parse --is-shallow-repository` deu
  `false` no começo. Não mexi em `dist\` nem em `C:\EditorImpressaoProva`.

## As regras que conferi

- **§11.12 (uma regra, um lugar):** cumprida para pôr o Visual C++, para "a saída leva o Visual C++?" e para os
  comandos das frases. Fica de fora "o Visual C++ é o oficial?", com duas réguas (achado 1).
- **§11.12.2 (nada dado como feito sem conferir):** cumprida na montagem (o tamanho do original conferido pela
  assinatura). Não cumprida na pasta pronta (achado 1).
- **§11.12.3 (a lista das falhas):** a do outro cobre a cópia cortada, o disco cheio e a pasta sem o Visual C++; faltam
  os caminhos 1 a 4 acima.
- **§11.12.4 e D-767:** o teste novo passa pela montagem de verdade, e a parte de mentira não é mais pronta que a de
  verdade. O vpk de verdade fica para a prova à vista.
- **§11.12.6 (ler a peça de fora):** nesta volta só o `shutil.copy2`; o caso do disco cheio conferido rodando.
- **§11.8 (o novo não estraga):** os 11 arquivos ao redor passam; nenhum teste antigo mudou.
- **§4.7 e D-811 (reversão):** confere (7 de 8). Das minhas 11 mutações, 7 acusadas.
- **D-815:** agente novo.
- **CLAUDE.md §10.9:** só criei arquivos dentro da minha pasta de rascunho e da pasta deste relatório. Não apaguei nada
  (ver "Para a gerente").

## Achados

1. **MÉDIO: a pasta pronta (`--pasta-pronta`) passa com um "Visual C++" que ninguém conferiu, sem a versão dele e sem o
   Tesseract, e é publicada.**
   - Onde: `empacotar.py:1710` (`conferir_pasta_pronta` só cobra `visual_c.is_file()`); `empacotar.py:1546` (a
     conferência do pacote cobra só o nome do Visual C++, não `vc_redist.versao.txt`); `publicar_versao_kaique.py:948`
     (com a pasta pronta, `pecas=None`, e a conferência do pacote não procura o Tesseract); a pasta de mentira dos testes
     antigos, `tests/test_publicar_versao.py:149` (`_pasta_pronta`: 11 bytes "MZ visual c", sem a versão, sem o
     Tesseract), é publicada pelos testes antigos (29 chamadas de `_publicar(a` no arquivo).
   - Lido na fonte: `atualizacao.py:1230` lê a versão de `vc_redist.versao.txt`; sem ele, vale "0.0.0".
     `preparar_o_computador` (rodado pela tarefa do Windows, como SYSTEM) chama `instalar_visual_c_se_faltar`, que roda
     o `vc_redist.x64.exe` do pacote.
   - Provado (sondas S1 e S1b, anexo `sondas6-resultado.txt`): a pasta de mentira passa na conferência e é publicada; o
     pacote sai **sem** `tesseract/`, **sem** a versão do Visual C++, e com os 11 bytes no lugar dele. No programa
     instalado, com um Visual C++ mais velho já no notebook, o programa nem tenta trocar e diz que deu certo (`True`).
   - Dedução (não rodei): sem nenhum Visual C++ instalado, a tarefa roda como SYSTEM o arquivo que veio na pasta, que
     ninguém conferiu. Sem o Tesseract, o achar texto do Kaique não funciona.
   - Por que médio, e não grave: só acontece com uma pasta feita à mão no PC do Samuel, e o pacote leva a assinatura
     dele. Por que não baixo: a montagem tem a conferência de verdade (`vc_redist_confere`, a assinatura da
     Microsoft) e a pasta pronta não; é a mesma regra com duas réguas (§11.12), e a pasta da prova de 20/11 convida a
     "só copiar o Visual C++" para não esperar os 4 minutos do PyInstaller.
   - Não é desta volta: já era assim em `b9300da8`. Mas a volta 6 chama `conferir_pasta_pronta` de "a função única de a
     pasta está pronta para o vpk" e diz que "a pasta pronta continua cobrada igual".
   - O que pedir: `conferir_pasta_pronta` cobrar da pasta pronta o mesmo que a montagem garante, pelos mesmos lugares:
     o Visual C++ pela `vc_redist_confere(assinatura_do_arquivo(...))` (a peça única que já existe), a
     `vc_redist.versao.txt` e o Tesseract (a lista de `_destinos_das_pecas` ou `conferir_tesseract`); e a conferência do
     pacote cobrar também a `vc_redist.versao.txt`. **Cuidado:** a pasta de mentira `_pasta_pronta` dos testes antigos
     deixaria de passar. Arrumá-la para ser como a de verdade é mudar um teste antigo: pede o "pode" do Samuel, como na
     D-817. Se a gerente preferir não mexer agora: na prova, nunca usar `--pasta-pronta` numa pasta arrumada à mão.

2. **BAIXO: o item 14 do roteiro da prova não dá para fazer depois do item 13.**
   - Onde: `relatorios/passo2-publicar/ONDE-PAREI.md:2001` (item 14) e `:1997` (item 13); `empacotar.py:919`
     (`construir_pasta` apaga `dist\EditorImpressao` antes de montar).
   - A pasta que a prova de 20/11 montou é `D:\programas\EditorImpressao\.claude\worktrees\passo2\dist\EditorImpressao`
     (lido no registro). O item 13 monta de novo **essa mesma pasta**. Depois dele, a pasta de 20/11 não existe mais.
   - Provado (sonda S5): depois do item 13, a pasta passa na conferência (agora tem o Visual C++), e o item 14 para em
     "a versão 1.1.0 já existe", não em "não tem o Visual C++". Quem olhar só o "PAREI" pode achar que o item 14 passou.
   - O que pedir: no roteiro, fazer o item 14 **antes** do 13 (o motor 1 já está publicado na pasta das provas, e a
     versão 1.1.0 ainda não: conferido em `C:\EditorImpressaoProva\versoes`).

3. **BAIXO: duas conferências do pacote depois do vpk não têm teste que as acuse.**
   - Onde: `empacotar.py:1546` (o Visual C++ em `esperados_no_pacote_do_velopack`, linha que a volta 6 mudou) e
     `publicar_versao_kaique.py:955` (`pecas = empacotar._PECAS`, que faz a conferência do pacote procurar o Tesseract).
   - Desliguei cada uma numa cópia (Z2 e Z4): `test_publicar_versao.py` (85) e `test_empacotar.py` (41) passam.
   - Por quê: o vpk de mentira copia a pasta inteira para o pacote; o que a pasta tem, o pacote tem. Só um vpk que
     deixasse algo de fora mostraria a conferência agindo.
   - Importa porque o outro escreve, em "De onde vem cada dado": "a prova é a conferência do pacote depois do vpk, que
     abre o pacote e procura o Visual C++". Essa prova não tem teste. Também "agora o teste novo percorre o Tesseract"
     (Ideias e bugs, volta 6): percorre, mas não acusa se a conferência sumir.
   - O que pedir: um teste com um vpk de mentira que deixa `instalar\` (ou `tesseract\`) de fora do pacote e cobra a
     recusa "o pacote do Velopack saiu errado". Um para cada.

4. **BAIXO: o empacotar chamado sozinho mexe na pasta antes de recusá-la.**
   - Onde: `empacotar.py:1616` (`preparar_saida` roda antes) e `:1619` (a conferência depois). Dentro de
     `preparar_saida`, `empacotar.py:1256` grava o `motor-exigido.json` e `:1258` apaga os zips de motor de `instalar\`.
   - Provado (sonda S3): uma pasta de fora sem o Visual C++, com um `instalar\motor-kraken-1.zip`, é recusada; depois da
     recusa, o zip sumiu e apareceu o `motor-exigido.json`.
   - Nenhum código chama assim hoje (o publicar confere antes, e para antes). Mas a conferência foi posta ali justamente
     para "quem chamasse esta função direto, com uma pasta de fora".
   - O que pedir: conferir a pasta **antes** de `preparar_saida` (a conferência não depende de nada que `preparar_saida`
     faz) e, se quiser, de novo depois.

5. **BAIXO: as aspas do caminho no comando da pasta não têm teste.**
   - Onde: `publicar_versao_kaique.py:315` (`--pasta "<pasta>"`), que serve à frase do motor e às frases do apagar.
   - Desliguei as aspas (Z6): 85 passam. As pastas dos testes não têm espaço no nome.
   - Hoje está certo, e a pasta da prova (`C:\EditorImpressaoProva\versoes`) não tem espaço. Uma pasta com espaço daria
     um comando que, seguido, não aponta para a pasta.
   - O que pedir: um caso com espaço no nome da pasta no teste do achado 2 do relatório 5 (o que segue a frase).

6. **OBSERVAÇÃO: o "lugar único" de pôr o Visual C++ não é cobrado por teste.**
   - Onde: `empacotar.py:1252` (`preparar_saida`). Fazê-la pôr o Visual C++ de novo (Z8) passa em 85 + 12 + 41 testes.
     Hoje não faz mal (o mesmo arquivo copiado duas vezes); o texto da função já diz que é arriscado. Só anotar.

7. **OBSERVAÇÃO: a frase do caminho de rede tem "(que tem função própria na peça)" para os testes antigos passarem.**
   - Onde: `core/windows.py:1153`. O outro escreve isso às claras. A frase fica longa, mas diz o motivo de verdade e não
     manda usar função que não existe. Mudar os testes antigos pediria o "pode" do Samuel. Não pede conserto.

8. **OBSERVAÇÃO: o teste mostra "assinatura da Microsoft conferida" para um arquivo de mentira.**
   - Onde: `empacotar.py:692` imprime a frase a partir das peças; no teste novo, as peças são trocadas e o arquivo é de
     mentira. Só a saída do teste diz isso; no uso de verdade, `juntar_pecas` confere antes. Não pede conserto.

9. **OBSERVAÇÃO: a ficha da versão guarda o commit, mas ninguém o lê.**
   - Onde: `empacotar.py:1704` (a conferência lê só a versão e a saída). Uma pasta feita com o código antigo passa como
     desta versão (sonda S2). Junto com o achado 1; se ele for consertado pela assinatura e pela versão do Visual C++, o
     caso da pasta de 20/11 arrumada à mão também para. Comparar o commit com o atual mudaria o uso normal (montar e
     depois fazer um commit de documento): fica como ideia, não pedido.

10. **OBSERVAÇÃO: a cópia do Visual C++ só confere o tamanho.**
    - Onde: `empacotar.py:1198`. Uma cópia corrompida do mesmo tamanho passaria. É muito improvável; o original foi
      conferido pela assinatura logo antes. Só anotar.

## O que falta para a prova à vista

1. A gerente decide se o achado 1 volta para quem escreveu antes da prova (ele pede o "pode" do Samuel para arrumar a
   pasta de mentira dos testes antigos).
2. Os itens 13 a 15 do roteiro **não bastam como estão**:
   - **fazer o item 14 antes do 13** (achado 2);
   - no item 13, além de ver `lib/app/instalar/vc_redist.x64.exe` dentro do pacote: ver também
     `lib/app/instalar/vc_redist.versao.txt` (com "14.44.35211.0") e que o `vc_redist.x64.exe` dentro do pacote tem o
     mesmo tamanho do baixado (uns 25 MB). As conferências do programa só olham o nome;
   - antes do item 13, olhar na linha "Visual C++: ..." de onde ele veio. Rodando da cópia `passo2`, ele vem de
     `D:\programas\EditorImpressao\.claude\worktrees\EditorImpressao-arquivos\ferramentas\downloads\` (o bug da Lista
     de bugs de 20/11). Se o arquivo sumir de lá, a montagem baixa da internet;
   - acrescentar: o item 6 (`--com-instalador`) **montado do zero**, e depois dele ver que
     `dist\EditorImpressao\instalar\` ficou só com o Visual C++ e a versão dele (o zip do motor tem de sair);
   - no item 15, seguir a frase ao pé da letra e ver o motor chegar na janela do servidor, e nada no GitHub.
3. O que só a publicação de verdade mostra, do vpk em diante: o vpk de verdade nunca recebeu uma pasta montada do zero
   por este caminho, nem uma com `instalar\` dentro. A assinatura, o envio e a leitura de volta são os mesmos das voltas
   anteriores, também nunca rodados de verdade pelo publicar. Os itens 4 a 12 do roteiro cobrem isso.

## Para a gerente: o que ficou fora do projeto

Tudo fica na pasta de rascunho desta conversa, em
`C:\Users\fotog\AppData\Local\Temp\claude\b9ca076ad002e817\14e42ebb-3236-41f4-94f5-20370c33bd91\scratchpad\quebra6\`:

- `antigo\` (o código de `b9300da8`, com os dois arquivos de teste de `3abf9acf` por cima), `novo\` (`3abf9acf`, onde
  rodaram as mutações; cada arquivo devolvido ao original, conferido) e `sonda\` (`3abf9acf`, com as minhas sondas no
  fim de `tests\test_publicar_versao.py`);
- os scripts e os resultados (`mutar_quebra6.py`, `mutacoes-resultado.txt`, `sondas-resultado.txt`,
  `reversao-no-codigo-antigo.txt`, `arredor.txt`) e o texto deste relatório.

**Um cuidado para a gerente:** a pasta de rascunho é a mesma da conversa do escritor, e a pasta `v6\` ao lado é dele.
No começo, extraí por engano o `git archive` de `3abf9acf` em cima de `v6\novo\`, que já era uma cópia de `3abf9acf`.
O conteúdo ficou igual (conferi com `diff -r`: só sobram as pastas `__pycache__` e `saida_teste` dele), nada foi
apagado. Também criei `v6\antigo\` e logo o movi para `quebra6\antigo\`. Fora isso não mexi em `v6\`.

O pytest cria as pastas dos testes em `C:\Users\fotog\AppData\Local\Temp\pytest-of-fotog\` (ele mesmo guarda só as
últimas). Não apaguei nada em lugar nenhum.
