# Passo 2 do plano da parte do Windows: sétima conferência de quem tentou quebrar (20/11/2026)

Sou um agente novo nesta volta (D-815). Não escrevi este código e não fiz as voltas anteriores. Não mexi no código do
outro.

O que **não** fiz:

- não rodei o publicar, o PyInstaller, o vpk nem o `gh release` de verdade (D-785, item 8);
- não pedi licença de administrador e não abri janela na tela do Samuel (a leitura da assinatura pela peça abre o
  PowerShell sem janela);
- não disparei rodada do GitHub (só consultei a 44816609032);
- não mexi em `C:\EditorImpressaoProva` nem na pasta `dist\EditorImpressao` da cópia `passo2` (só li).

Tudo rodou em cópias do código (`git archive` de `db4b377a` e de `25c514ad`), na pasta de rascunho desta conversa
(`quebra7\`), um arquivo de teste por vez (com uma exceção pequena, contada em "Para a gerente").

## Pedido

- Papel: quebrador
- Commit de partida: eda1dc6b
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
três formatos, e a pasta `anexos-7/`. O pacote `anexos/pacote-quem-quebra-volta7.md`, que a gerente gerou, vai no mesmo
commit, como ela pediu.)

## Veredito

**PRONTO PARA CONFERIR (a prova à vista): o defeito médio da volta anterior está consertado pela causa, a pasta já
montada agora é recusada pelos mesmos motivos da montada do zero, e nada do que funcionava quebrou. Ficam 5 baixos:
quatro proteções novas que nenhum teste acusa (a mesma família de erro da volta anterior) e um item do roteiro da prova
escrito numa ordem que não dá para seguir.** Nada disso muda o que o Kaique recebe hoje.

O que está certo:

- **A pasta já montada é conferida igual à montada do zero.** Uma função só (`conferir_pasta_pronta`) cobra o Visual
  C++ pela assinatura da Microsoft, o arquivo da versão dele e cada arquivo do Tesseract. Testei com arquivos de
  verdade, lidos pelo próprio Windows: o Visual C++ oficial passa; um arquivo de outro programa da Microsoft, o Visual
  C++ de 32 bits, o Visual C++ novo (14.50), o oficial cortado, o oficial com bytes a mais no fim e o oficial com um byte
  trocado são recusados.
- **A leitura da assinatura que falha nunca vira "passou".** O PowerShell que não termina, a resposta vazia, a resposta
  sem os campos e a resposta só com "Valid": a pasta e a montagem recusam nos quatro casos.
- **A prova de reversão confere.** Os testes novos no código antigo: 10 de 13 falham no arquivo do publicar (os 9 que o
  outro contou e o do arquivo do Tesseract vazio, que ele acrescentou depois); os 3 que passam cobram proteções que já
  existiam. O teste novo do empacotar falha lá só porque a função nova não existia.
- **Os testes antigos não ficaram mais frouxos.** Só mudaram as três peças que a D-818 permite e o outro listou (a pasta
  de mentira, a leitura da assinatura na preparação e uma opção nova do vpk de mentira, desligada). Os 88 antigos com a
  pasta nova passam também no código antigo.
- **Os 4 baixos do relatório 6 foram consertados pela causa** (detalhe em "O que conferi").

O que fica (5 baixos): achados 1 a 5. Pela D-775, a gerente decide se os testes que faltam (achados 1 a 4) voltam a quem
escreve antes da prova à vista. O catálogo dos erros manda pedir o conserto pela causa quando a mesma família aparece em
duas voltas seguidas do mesmo passo, e é o caso (achados 3 e 5 do relatório 6, achados 1 a 4 aqui). Nunca "aprovado":
só o Samuel aprova.


## Decisões que esta tarefa precisa cumprir

O pacote diz "D-815 a D-818: NÃO ACHADA NO LIVRO". Achei as quatro no Livro da `obra-juncao` (linhas 1105 a 1108) e li
inteiras, com as outras 11 pedidas.

- D-818 "vai ter que reprogramar?" · "A". Aqui: **cumprida no que a decisão pede.** A pasta já montada passa pela mesma
  função da montada do zero e é recusada, antes do vpk, sem o Tesseract, com um Visual C++ que não é o oficial ou sem o
  arquivo da versão dele (testes do outro e minhas sondas com arquivos de verdade). A montada do zero continua passando.
  Os testes antigos mudaram só nas peças que o outro listou, e nenhum passou a cobrar menos (conferido abaixo). O que
  falta não é da decisão, é de teste: quatro proteções novas sem teste que as acuse (achados 1 a 4).
- D-605 "A partir de agora, nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já está
  escolhido e testado [...]". Aqui: os 10 arquivos de teste ao redor passam no código novo (lista em "O que conferi");
  a única troca de teste antigo é a que a D-818 autoriza.
- D-727 "pode, se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador né". Aqui: o Visual C++
  oficial, a versão dele e o Tesseract são cobrados de toda pasta antes do vpk e de todo pacote depois do vpk. As
  licenças do Tesseract também são cobradas, mas sem teste (achado 3).
- D-767 "não faça mais nada escodindo ou de mentira". Aqui: a leitura da assinatura é a peça de verdade do Windows. Nos
  testes do publicar, só os dois conteúdos de prova respondem "Microsoft"; o resto vai à leitura de verdade. O caminho
  certo com o Visual C++ oficial só rodou de verdade na minha sonda, no PC (no GitHub o arquivo não existe).
- D-773 "A". Aqui: a frase com a pasta das provas com espaço no nome ganhou teste (achado 5 do relatório 6).
- D-775 "ok". Aqui: tentei quebrar, sem pergunta do Windows. O resultado vai à gerente.
- D-776, D-777, D-788, D-789, D-795: nada desta volta toca a conta do espaço, o .msi, o motor, a diferença nem o
  Setup.exe (conferido no diff).
- D-785 (item 8, publicar sempre à vista). Aqui: não rodei o publicar de verdade.
- D-815 "ok". Aqui: sou um agente novo nesta volta, sem memória da anterior. O escritor desta volta estava na segunda e
  última volta dele.
- D-816 "A , mas onde estamos antes de você fazer qualquer processo" e D-817 "pode". Aqui: nada desta volta toca o
  liberar nem o apagar; os `test_d816_*` passam no arquivo inteiro (98 de 98).

## O que li

- `.claude/agents/verificador.md` e o `CLAUDE.md` inteiro (na cópia `passo2`; ela é mais antiga que a do projeto só na
  parte da Central), com atenção ao §4.7, §11.8, §11.12 (os 6 pontos) e §11.13.
- `memoria/INDICE.md` (na cópia `passo2`), `memoria/geral/atualizador.md` (só existe na pasta do projeto,
  `D:\programas\EditorImpressao\memoria\geral\atualizador.md`; na cópia `passo2` e na `obra-juncao` não há) e o catálogo
  dos erros (`obra-juncao`, famílias F1 a F10).
- O meu pacote (`anexos/pacote-quem-quebra-volta7.md`) e, no Livro da `obra-juncao`, as linhas inteiras de D-605, D-727,
  D-767, D-773, D-775, D-776, D-777, D-785, D-788, D-789, D-795, D-813, D-815, D-816, D-817 e D-818.
- No ONDE-PAREI do escritor, todas as partes "Volta 7": "Onde parei", decisões, "O que já está escolhido e testado
  aqui" (a lista dos testes antigos mudados), "Como fica para quem usa", "A causa, a regra e todos os caminhos" (a tabela
  dos 7 caminhos), "O que pode falhar", "O que li", "O que foi feito", "Testes", "Caminho e função", "Cada proteção", "De
  onde vem cada dado", "Ressalvas", "Ideias e bugs", "O que o agente que tentou quebrar achou" e "A prova de verdade"
  (itens 1 a 17).
- O relatório 6 de quem tentou quebrar e os anexos `reversao-volta7-*` do escritor.
- O código: `git diff db4b377a eda1dc6b` inteiro (só `empacotar.py`, `publicar_versao_kaique.py` e dois arquivos de
  teste mudaram; de `25c514ad` a `eda1dc6b` nenhum `.py` muda). Li inteiras, no código novo: `assinatura_do_arquivo`,
  `vc_redist_confere`, `conferir_o_visual_c`, `preparar_vc_redist`, `juntar_pecas`, `_avisar_pecas_faltando`,
  `_destinos_das_pecas`, `relativos_do_tesseract`, `conferir_tesseract`, `preparar_pasta_para_o_velopack`,
  `preparar_saida`, `esperados_no_pacote_do_velopack`, `proibidos_no_pacote_do_velopack`, `conferir_pacote_do_velopack`,
  `construir_pacote_do_velopack`, `conferir_pasta_pronta` (empacotar); `publicar` (publicar); `ler_assinatura_digital`,
  `rodar_powershell`, `Resposta` (peça do Windows); `precisa_do_visual_c` e `instalar_visual_c_se_faltar` (atualizacao);
  `_montar_comando` e a procura do Tesseract (`core/ocr_tesseract.py`). E os testes novos e os três trechos antigos
  mudados, inteiros, comparados com os de `db4b377a`.
- A pasta `dist\EditorImpressao` da cópia `passo2` (a da prova de 20/11), só lida: a lista do Tesseract e a ficha.
- Peça de fora: nada novo nesta volta. O que conferi rodando: o `Get-AuthenticodeSignature` do Windows (pela peça) em
  arquivos de verdade (ver "O que conferi"). Li a página da Microsoft dos Visual C++ mais novos (fonte no fim) e
  perguntei ao endereço permanente que o programa usa para onde ele leva (só o cabeçalho, sem baixar).

## O que conferi nas falhas, nas peças de fora e nos caminhos

### A prova de reversão (anexo `anexos-7/reversao-no-codigo-antigo.txt`)

- Os dois arquivos de teste de `eda1dc6b` por cima do código de `db4b377a`, numa cópia minha. Arquivo do publicar, só os
  testes novos: **10 falham e 3 passam.** Falham os 6 casos da D-818 (o do arquivo do Tesseract vazio, que o outro
  acrescentou depois de contar "9 de 12", também falha), 3 dos 4 casos do pacote sem uma peça e o do empacotar chamado
  sozinho. Passam: o pacote sem o Visual C++, o montado do zero sem o Tesseract e a pasta com espaço no nome. Os três
  cobram proteções que já existiam (servem para a proteção não sumir calada, não para provar um defeito).
- O teste novo do empacotar falha no código antigo só porque a função nova não existia (`AttributeError`). No código
  antigo a montagem já usava uma régua só, escrita duas vezes dentro da mesma função. Ele não prova um defeito.
- O arquivo inteiro no código antigo: 10 falham (os novos) e **88 passam** (os antigos, com a pasta de mentira nova),
  como o outro escreveu. No código novo: **98 de 98 passam.**

### Os testes antigos mudados ficaram mais frouxos? (anexo `anexos-7/testes-antigos-sem-mudanca-no-codigo-novo.txt`)

Comparei cada função do arquivo de testes em `db4b377a` e em `eda1dc6b`. Só mudaram três trechos, os que o outro
listou: a pasta de mentira (`_pasta_pronta`), a preparação (`ambiente`) e o vpk de mentira (`VPK_FALSO`). O resto só
foi acrescentado no fim.

- **A pasta de mentira** ganhou o arquivo da versão do Visual C++ e os 35 arquivos do Tesseract (pela lista da
  montagem). Só peças a mais: nenhum teste antigo perdeu um caso. O teste novo da D-818 confere que essa pasta inteira
  passa na conferência; então, quando um teste antigo espera uma recusa, ela vem do motivo dele, não da conferência nova.
- **A preparação** passou a responder "assinado pela Microsoft" só para dois conteúdos exatos (os dois Visual C++ de
  prova, comparados por igualdade, não por pedaço). O arquivo antigo de testes nunca falava da assinatura, então nenhum
  teste antigo deixou de ler algo de verdade que lia antes.
- **O vpk de mentira** ganhou uma opção desligada de fábrica; com ela vazia, o código dele é o mesmo.
- **Prova de que a troca era necessária e só para isso:** o arquivo de testes antigo, sem mudança nenhuma, no código
  novo: 41 falham, todos pela conferência nova ("o Visual C++ da pasta ... não é o oficial da Microsoft: ... o Windows
  diz: UnknownError" para os 11 bytes de mentira, e "não tem o Tesseract inteiro"). Os outros 44 passam.
- **Os testes antigos que esperam uma recusa sem dizer qual** (`pytest.raises(pub.Parou)` sem a frase): olhei cada um.
  Ou não usam a pasta, ou conferem depois o que esperam (ex.: o do .msi confere que as duas passadas do vpk rodaram).

Leitura: a D-818 permitia "os testes antigos que usam a pasta de mentira sem essas peças passam a trazê-las". A troca da
leitura da assinatura na preparação vai um pouco além da letra (não é uma peça da pasta), mas é o que faz o arquivo de
poucos bytes "ser" o Visual C++ de verdade; o outro escreveu isso às claras. Não achei teste que passou a cobrar menos.
Deixo a leitura da letra da D-818 para a gerente (observação 9).

### O Visual C++ falso: arquivos de verdade, lidos pelo Windows (anexos `sonda-assinaturas.txt`, `sondas7-resultado.txt`)

Copiei para a minha pasta (só lendo os originais) o `vc_redist.x64.exe` da pasta de downloads, os dois Visual C++ que o
Windows guardou no PC (14.50, de 32 e de 64 bits) e um programa assinado pela Microsoft (o "Copilot Update"). Fiz três
estragos do oficial. Cada um, posto como `instalar\vc_redist.x64.exe` numa pasta já montada, lido pela peça de verdade:

| O arquivo | O que o Windows diz | A conferência da pasta |
|---|---|---|
| o oficial (14.44.35211.0) | assinatura válida, da Microsoft, Visual C++ 2015-2022 x64 | **passa** |
| outro programa da Microsoft | válida, da Microsoft, produto "Copilot Update" | recusa |
| o Visual C++ de 32 bits | válida, produto "(x86)" | recusa |
| o Visual C++ novo de 64 bits (14.50) | válida, produto "v14 Redistributable (x64)" | recusa (observação 7) |
| o oficial cortado na metade | sem assinatura | recusa |
| o oficial com 4 KB a mais no fim | sem assinatura | recusa |
| o oficial com um byte trocado no meio | a assinatura não bate com o arquivo | recusa |
| uma cópia do `powershell.exe` do Windows | válida, assinante "CN=Microsoft Windows" | a régua recusa pelo assinante (rodada no original; a cópia lida dá a mesma assinatura válida; ver achado 1) |

**Lido na fonte:** a régua (`vc_redist_confere`) exige a assinatura válida, o assinante "CN=Microsoft Corporation, O=Microsoft
Corporation", o produto "Microsoft Visual C++ 2015-20xx Redistributable (x64)" e a versão começando por "14.".

### A leitura da assinatura que falha (anexo `sondas7-resultado.txt`, SONDA7-4)

Troquei só a conversa com o PowerShell da peça por quatro respostas ruins: não terminou no tempo; resposta vazia;
resposta sem os campos; resposta só com "Valid". Nos quatro, a pasta é recusada ("a assinatura digital não confere" ou
"não foi assinado pela Microsoft") e a montagem recusa o arquivo da pasta de downloads. **Nada vira "passou".** Lido na
fonte: `assinatura_do_arquivo` transforma a falha em "erro: ...", e a régua nunca aceita isso.

### O arquivo da versão do Visual C++ (SONDA7-3)

A conferência e o programa instalado leem esse arquivo com código diferente (achado 6). Testei cinco conteúdos com o
Visual C++ oficial: com a marca de UTF-8 no começo (recusado), com quebra de linha do Windows no fim (passa; o programa
instalado lê certo), em UTF-16 (recusado; o programa instalado levantaria erro), vazio (recusado) e com espaços em volta
(passa; lido certo). **Hoje, tudo o que passa na conferência o programa instalado lê certo.**

### O Tesseract (lido na fonte e na pasta da prova)

- A lista única (`relativos_do_tesseract`) tem os 27 arquivos, as duas licenças e os seis idiomas. A pasta da prova de
  20/11 tem exatamente esses 35, mais o `LEIA-ME-TESSERACT.txt` (o texto que a montagem escreve; não é do Tesseract).
- O programa chama o Tesseract só com esses arquivos: `tesseract.exe`, as DLLs, `--tessdata-dir` apontando para
  `tesseract\tessdata` e o hOCR ligado pelo `-c` (o arquivo de configuração `configs\hocr` não é usado; `core/ocr_tesseract.py`,
  `_montar_comando`). **A lista cobre o que o programa usa.**
- A conferência nova, rodada na pasta da prova de 20/11 (só lendo): "não tem o Visual C++ em instalar\" e nada sobre o
  Tesseract. Isso também confere o item 13 do roteiro novo.
- O conteúdo não é comparado: um Tesseract de 1 byte por arquivo passa (SONDA7-5). O outro escreveu isso nas ressalvas.

### Os caminhos até o vpk (a tabela do outro, conferida um por um no código)

| Caminho | Passa pela mesma conferência antes do vpk? | O que vi |
|---|---|---|
| publicar montado do zero | sim, cedo e de novo antes do vpk | a montagem confere o Visual C++ pela mesma régua (`preparar_vc_redist` → `conferir_o_visual_c`) |
| publicar `--pasta-pronta` | sim, cedo (antes da conta do espaço) e antes do vpk | pela mesma função; a mutação W6 (pular só a pasta pronta) é acusada |
| a segunda passada (o instalador) | sim, agora antes de `preparar_saida` | entre as passadas só muda o arquivo do motor; o pacote depois confere o motor |
| a volta da pasta depois do instalador | não vai ao vpk (só tira o zip do motor, também com erro) | igual à volta 6 |
| `construir_pacote_do_velopack` chamado sozinho | sim, antes de mexer na pasta | o teste novo prova que a pasta recusada fica igual, arquivo por arquivo |
| a pasta portátil e o Inno | não vão ao vpk; não passam por esta conferência | o Inno usa a mesma lista do Tesseract (`_destinos_das_pecas` → `relativos_do_tesseract`) |
| o pacote depois do vpk | sempre: o Tesseract pela lista, o Visual C++ e a versão dele | só confere que cada nome está lá, não o tamanho (o roteiro manda olhar o tamanho, item 15) |

Procurei outras listas do Tesseract e outras réguas do Visual C++ em todo o código fora dos testes: não há (a lista de
nomes só existe em `empacotar.py`; a régua só em `conferir_o_visual_c`).

### Os 4 baixos do relatório 6: consertados pela causa?

- **Item 14 do roteiro depois do 13:** a ordem foi trocada (a pasta antiga primeiro). Mas o novo item 14 tem um passo
  que não dá para fazer onde está (achado 5).
- **Duas conferências do pacote sem teste:** sim. O vpk de mentira agora deixa uma peça de fora e o publicar para em "o
  pacote do Velopack saiu errado". A Z2 do relatório 6 seria acusada pelo caso do pacote sem o Visual C++ (dedução: não a rodei); a Z4
  deixou de ter efeito, porque o pacote agora cobra o Tesseract com ou sem as peças, e a R6 do outro (tirar essa
  cobrança) é acusada. Faltou o caso das licenças (achado 3).
- **O empacotar chamado sozinho mexia na pasta antes de recusar:** sim, pela causa (a conferência vem antes) e com teste
  que compara a pasta inteira antes e depois.
- **As aspas sem teste:** sim, teste com espaço no nome que segue as duas frases ao pé da letra.

### As mutações minhas (anexo `anexos-7/mutacoes7-resultado.txt`; script `mutar_quebra7.py.txt`)

Numa cópia de `25c514ad`, uma por vez, o arquivo devolvido ao original depois de cada uma (conferido byte a byte).
Rodei os arquivos de teste inteiros. Diferentes das R1 a R12 do outro, das Y da volta 6 e das Z do relatório 6.

| | O que desliguei | Acusada? |
|---|---|---|
| W1 | a conferência da pasta com régua própria: aceita qualquer arquivo com assinatura válida, de quem for | **não** (98 + 42 passam) |
| W2 | a conferência da pasta deixa de cobrar as licenças do Tesseract | **não** (98 + 42) |
| W3 | a conferência do pacote depois do vpk deixa de cobrar as licenças do Tesseract | **não** (98 + 42 + 38) |
| W4 | a versão do arquivo comparada por "começa com" (o arquivo vazio passa) | **não** (98 + 42) |
| W5 | a leitura da assinatura que falha vira "passou" na régua única | **não** (98 + 42) |
| W6 | o publicar não confere cedo só a pasta pronta (desvio para um caso) | sim (7 testes) |

**1 de 6 acusadas.** As 5 que passam estão nos achados 1 a 4. Com a W5, mostrei rodando (anexo `sonda-w5-resultado.txt`)
o que ela deixaria passar: a montagem aceita o Visual C++ sem ler a assinatura, grava a versão vazia, a conferência da
pasta compara vazio com vazio e passa, e o programa instalado, num notebook com um Visual C++ mais velho, nunca instala
o novo.

### O que já funcionava em volta (§11.8; anexo `anexos-7/arredor.txt`)

Código de `25c514ad`, um arquivo por vez: `test_publicar_versao.py` 98; `test_empacotar.py` 42; `test_publicar_motor.py` 12; `test_windows_peca.py` 69 e 2 pulados; `test_publicar_servidor.py` 14; `test_windows_janela_de_prova.py` 10; `test_decisoes_atualizacao.py` 38; `test_decisoes_ajudante_da_atualizacao.py` 37; `test_decisoes_testes_a_distancia.py` 13; `test_nome_do_pacote.py` 5. Todos passam.

### A rodada do GitHub 44816609032

Consultei: tentativa 1, **success**, todas as partes (as 5 da suíte, os botões e os prints da janela real, o porteiro: "CONFERIDO"); o filtro de velocidade não foi pedido nesta rodada. O registro diz "código trocado pelo de passo2-publicar-2026-11-19 (eda1dc6b...)": é o código desta volta (de `25c514ad` a `eda1dc6b` nenhum `.py` muda). Lá, `test_publicar_versao.py` deu 98 passados (o caso do Visual C++ falso lido pela peça de verdade também roda no Windows do GitHub) e `test_empacotar.py` 41 passados e 1 pulado (o que precisa do Tesseract instalado).

## Caminhos que o outro não listou

1. **A leitura que falha, dentro da régua única:** a tabela do outro diz que a falha "nunca confere", e é verdade no
   código, mas o caminho "leitura falha → montagem → versão vazia → conferência" não tem teste (achado 1, W5).
2. **Um arquivo com assinatura válida que não é da Microsoft Corporation chegando à conferência da pasta:** o teste novo
   só usa um arquivo sem assinatura, que qualquer régua recusa (achado 1, W1).
3. **As licenças do Tesseract** no caminho da pasta pronta e no pacote (achado 3).
4. **O item 14 do roteiro:** a linha que ele manda ler só aparece durante a montagem (achado 5).

## Falhas não pensadas e resultado não conferido

- **Proteção sem teste (F3), de novo:** a leitura que falha (W5), a régua da pasta (W1), as licenças (W2, W3) e a
  versão vazia (W4). O código de hoje faz o certo em todas (provei rodando); só nenhum teste acusa se alguém mudar.
  É a mesma família dos achados 3 e 5 do relatório 6.
- **O escrito não bate (F7), pequeno:** o teste novo do empacotar diz "um arquivo sem assinatura é recusado pelos dois"
  (montagem e conferência da pasta), mas não chama a conferência da pasta (achado 1). O item 14 do roteiro diz "ainda
  antes de montar" para uma linha que a montagem imprime (achado 5).
- **Conta duplicada (§11.12):** o arquivo da versão do Visual C++ é lido de dois jeitos (achado 6).
- **Dá como feito o que não conferiu (F5):** não achei. A conferência lê a assinatura do arquivo que está na pasta, não
  uma anotação.
- **F9 (mexer no que é do Samuel sem ele ver):** nada. `git rev-parse --is-shallow-repository` deu `false`. Não criei
  junção. Não mexi em `dist\` nem em `C:\EditorImpressaoProva`.

## As regras que conferi

- **§11.12 (uma regra, um lugar):** cumprida para "é o Visual C++ oficial?" (uma função, usada pela montagem e pela
  pasta) e para "o que é o Tesseract" (uma lista, usada pela montagem, pelo Inno, pela pasta e pelo pacote). Não
  cumprida para "que versão o arquivo diz" (achado 6). A prova de "o mesmo resultado nos dois caminhos" existe, mas não
  pega uma régua diferente na pasta (achado 1).
- **§11.12.2 (nada dado como feito sem conferir; falha nunca vira "deu certo"):** cumprida no código (SONDA7-4); sem
  teste (achado 1).
- **§11.12.3 (a lista das falhas):** a do outro cobre os casos da D-818 e o da leitura que falha; faltam os caminhos 1 a
  4 acima.
- **§11.12.4 e D-767:** a régua roda pela peça de verdade nos testes para os arquivos falsos; o caminho certo só na minha
  sonda e na prova à vista.
- **§11.12.6 e D-813 (ler a peça de fora; todos os jeitos que ela aceita):** a régua compara a assinatura de verdade e o
  nome de quem assinou (o texto do certificado); conferi os vizinhos que existem no PC (ver a tabela). Ver a observação
  7 sobre o nome do produto.
- **§11.8 e D-818 (o novo não estraga; os testes antigos só ganham peças):** conferido acima, sem afrouxar.
- **§4.7 e D-811 (reversão):** confere (10 de 13 no publicar; o do empacotar não prova defeito). Das minhas 6 mutações,
  1 acusada.
- **§11.4 (a prova da decisão em `tests/test_decisoes*.py`):** a prova da D-818 está em `tests/test_publicar_versao.py`;
  o outro escreveu por quê (observação 10).
- **D-815:** agente novo.
- **CLAUDE.md §10.9:** só criei arquivos na minha pasta de rascunho e na pasta deste relatório, com uma exceção (ver "Para
  a gerente"). Não apaguei nada.

## Achados

1. **BAIXO: duas proteções do Visual C++ não têm teste que as acuse: a leitura que falha e "a mesma régua" na pasta.**
   - Onde: `empacotar.py`, `assinatura_do_arquivo` e `conferir_o_visual_c` (a falha vira "erro: ...", que a régua
     recusa); `conferir_pasta_pronta` (chama `conferir_o_visual_c`).
   - Lido na fonte: hoje está certo. Provado rodando: a leitura que falha recusa nos quatro jeitos (SONDA7-4), e um
     arquivo válido de outro assinante é recusado (a cópia do `powershell.exe`).
   - Provado (mutações): **W5** (a leitura que falha vira "passou") e **W1** (a pasta com régua própria, que aceita
     qualquer assinatura válida) passam em todos os testes. O teste novo da D-818 usa só um arquivo sem assinatura, que
     qualquer régua recusa. O teste novo do empacotar diz que confere "os dois", mas não chama a conferência da pasta.
   - O que a W5 deixaria passar (rodado, `sonda-w5-resultado.txt`): a montagem grava a versão vazia, a conferência
     compara vazio com vazio e passa, e o programa instalado com um Visual C++ mais velho nunca instala o novo.
   - Por que baixo: o código de hoje faz o certo; é a proteção que pode sumir calada.
   - O que pedir: (a) um teste que faça a leitura falhar (a peça do PowerShell respondendo "não terminou") e cobre a
     recusa da pasta e da montagem; (b) um teste que ponha uma **cópia do `powershell.exe` do Windows** como
     `instalar\vc_redist.x64.exe` e na pasta de downloads, e cobre a mesma recusa nos dois. Esse arquivo existe em todo
     Windows e tem assinatura válida (conferi a cópia no PC: "Valid", assinante "CN=Microsoft Windows"), então roda de
     verdade também no GitHub (dedução: não rodei lá).

2. **BAIXO: a versão do Visual C++ comparada inteira não tem teste para o arquivo vazio ou com só um pedaço.**
   - Onde: `empacotar.py`, `conferir_pasta_pronta` (`lida != versao_do_vc`).
   - Provado: a W4 (comparar por "começa com") passa em todos os testes; o único caso de teste é uma versão inteira e
     diferente ("14.29.30133.0"). Hoje o arquivo vazio é recusado (SONDA7-3).
   - O que pedir: um caso "arquivo da versão vazio" no teste da D-818.

3. **BAIXO: as licenças do Tesseract são cobradas, mas nenhum teste acusa se deixarem de ser.**
   - Onde: `conferir_pasta_pronta` e `esperados_no_pacote_do_velopack` (as duas pela lista única, que tem `LICENSE` e
     `AUTHORS`).
   - Provado: W2 (a pasta) e W3 (o pacote) passam em todos os testes. Hoje a pasta sem a `LICENSE` é recusada (SONDA7-7).
   - Por que importa: a licença do Tesseract tem de ir junto com ele.
   - O que pedir: um caso "sem a licença do Tesseract" no teste da D-818 e um `tesseract/LICENSE` no teste do pacote sem
     uma peça.

4. **BAIXO: a mesma família de erro (proteção sem teste) em duas voltas seguidas.**
   - O relatório 6 achou 3 (achados 3 e 5, observação 6); esta volta, 5 (W1 a W5). O outro fez 12 mutações e 11 foram
     acusadas; elas desligavam cada proteção inteira, e nenhuma tirava uma condição de dentro da régua (quem assinou, a
     falha da leitura) nem um item da lista (as licenças).
   - O catálogo dos erros manda a gerente pedir o conserto pela causa quando isso acontece. Sugestão para o pedido: para
     cada proteção nova, uma mutação que **tira uma condição de dentro dela** (não só a desliga inteira), e o teste que
     a acusa.

5. **BAIXO: o novo item 14 do roteiro da prova não dá para fazer onde está.**
   - Onde: `relatorios/passo2-publicar/ONDE-PAREI.md`, "A prova de verdade", Volta 7, item 14: "Ainda antes de montar, ler
     na linha "Visual C++: ..." de onde ele vem."
   - Lido na fonte: essa linha só é impressa pela própria montagem, no começo dela (`empacotar.py`,
     `_avisar_pecas_faltando`, chamada por `construir_pasta`). Antes do item 15 ela não aparece.
   - O que pedir: trocar por "no item 15, logo no começo (antes de o PyInstaller começar), ler a linha 'Visual C++: ...'";
     ou, antes do item 15, olhar se o arquivo está na pasta de downloads da cópia `passo2` (está: 25.635.768 bytes, o
     mesmo do endereço da Microsoft, conferido pela soma).
   - O item 13 novo está certo: rodei a conferência nova na pasta da prova de 20/11 (só lendo), e ela diz só "não tem o
     Visual C++ em instalar\".

6. **BAIXO: o arquivo da versão do Visual C++ é lido de dois jeitos (§11.12, conta duplicada).**
   - Onde: `empacotar.py`, `conferir_pasta_pronta` (lê com troca dos caracteres ruins e tira os espaços);
     `atualizacao.py`, `instalar_visual_c_se_faltar` (lê sem troca e tira os espaços). Quem escreve é
     `preparar_pasta_para_o_velopack`.
   - Provado: hoje concordam em tudo o que testei (SONDA7-3): o que a conferência aceita, o programa instalado lê certo.
   - Por que baixo: a §11.12 pede "um dado é lido e gravado por uma função só". Se alguém mudar só um dos dois, a
     conferência passa a aceitar o que o programa do Kaique lê errado (e o programa, quando lê errado, decide não instalar
     o Visual C++).
   - O que pedir: uma função só em `atualizacao.py` que lê a versão do pacote, usada pelo programa instalado e pela
     conferência.

7. **OBSERVAÇÃO: a régua do Visual C++ recusa o Visual C++ novo da Microsoft e aceitaria um oficial mais velho.**
   - Lido na fonte: o nome do produto tem de ser "Microsoft Visual C++ 2015-20xx Redistributable (x64)". O Visual C++
     14.50 (que já está neste PC, guardado em `C:\ProgramData\Package Cache`) chama-se "Microsoft Visual C++ v14 Redistributable (x64)" e é
     recusado. Um oficial de 2015-2019 (14.2x) passaria (dedução pelo nome; não tenho o arquivo).
   - Hoje não faz mal: o endereço permanente que o programa usa (`aka.ms/vs/17/release`) ainda leva ao 14.44, o mesmo
     arquivo da pasta de downloads (conferi a soma no endereço, sem baixar). A Microsoft passou a indicar outro endereço
     para os novos (fonte no fim).
   - Não é desta volta (a régua já existia na montagem). Para a Lista de espera: decidir a versão mínima e o nome novo.

8. **OBSERVAÇÃO: o caminho certo com o Visual C++ oficial lido de verdade não roda em nenhum teste automático.**
   - Os testes dão o Visual C++ de prova como "da Microsoft" (necessário: no GitHub o arquivo não existe). Só a minha
     sonda (SONDA7-1) e a prova à vista (item 15) passam por ele. Rodou e passou na sonda.
   - Ideia: um teste que roda só onde o arquivo existe (o PC) e pula no GitHub, dizendo que pulou.

9. **OBSERVAÇÃO: a troca da leitura da assinatura na preparação dos testes vai um pouco além da letra da D-818.**
   - A D-818 autoriza "os testes antigos que usam a pasta de mentira sem essas peças passam a trazê-las". A troca na
     preparação não é uma peça da pasta; é o que faz os poucos bytes "serem" o Visual C++. Não afrouxou nenhum teste
     (conferido acima). A gerente decide se basta a lista que o outro escreveu ou se leva ao Samuel.

10. **OBSERVAÇÃO: a prova da D-818 não está em `tests/test_decisoes*.py`** (CLAUDE.md §11.4). O pacote do escritor não
    deixava mexer nesse arquivo; ele escreveu isso nas ressalvas. É da gerente.

11. **OBSERVAÇÃO: o Tesseract da pasta já montada é conferido pela existência e pelo tamanho, não pelo conteúdo.** Um
    arquivo de 1 byte passa (SONDA7-5). O outro escreveu isso nas ressalvas; só confirmo rodando.

## O que falta para a prova à vista

1. A gerente decide se os achados 1 a 4 (só testes) e o 6 voltam a quem escreve antes da prova. Nenhum muda o que a
   prova vai ver.
2. No roteiro: o item 14 como no achado 5.
3. No item 15, além do que já está: conferir que o `vc_redist.versao.txt` dentro do pacote diz exatamente
   "14.44.35211.0" (é o que o programa do Kaique lê para decidir se instala).
4. O que só a publicação de verdade mostra: a leitura da assinatura pela peça dentro do publicar (2 ou 3 vezes por
   publicação, uns segundos cada, não medido), o vpk de verdade recebendo uma pasta com `instalar\` e o Tesseract, e o
   tamanho do Visual C++ dentro do pacote (as conferências do programa olham só o nome).

## Para a gerente: o que ficou fora do projeto

Na pasta de rascunho desta conversa, em
`C:\Users\fotog\AppData\Local\Temp\claude\b9ca076ad002e817\14e42ebb-3236-41f4-94f5-20370c33bd91\scratchpad\quebra7\`:

- `antigo\` (o código de `db4b377a`, com os dois arquivos de teste de `eda1dc6b` por cima), `novo\` (`25c514ad`, onde
  rodaram as mutações; cada arquivo devolvido ao original, conferido), `novo-testes-velhos\` (`25c514ad` com o arquivo
  de testes antigo, sem mudança), `sonda\` (`25c514ad`, com as minhas sondas no fim de `tests\test_publicar_versao.py`) e
  `w5\` (`25c514ad` com a mutação W5 aplicada **e deixada**, só para a sonda dela; não serve para nada além disso);
- `pecas\`: cópias do Visual C++ oficial, dos dois Visual C++ que o Windows guardou em `C:\ProgramData\Package Cache`,
  do `CopilotUpdate.exe` e do `powershell.exe`, e os três estragos do oficial (os originais só foram lidos);
- os scripts e os resultados (os mesmos de `anexos-7/`).

**Um arquivo meu ficou fora da pasta de rascunho:** a sonda da W5 criou uma pasta temporária
`C:\Users\fotog\AppData\Local\Temp\w5-f5nn64f9\` (uma cópia do Visual C++ oficial e uma pasta do programa de mentira, uns
25 MB). Não apaguei (fora do projeto). A gerente decide.

**Uma vez rodei duas coisas ao mesmo tempo:** a sonda da W5 (um script, não um arquivo de teste) rodou enquanto a
última mutação rodava o arquivo de testes do publicar. Não mudou o resultado de nenhuma das duas (a W6 foi acusada; a
sonda não usa a cópia das mutações).

O pytest cria as pastas dos testes em `C:\Users\fotog\AppData\Local\Temp\pytest-of-fotog\` (ele mesmo guarda só as
últimas). Não apaguei nada em lugar nenhum.

## Fontes de fora

- Microsoft, "Latest supported Visual C++ Redistributable downloads":
  https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist (o endereço novo `aka.ms/vc14/...` para os
  14.50).
- O endereço `https://aka.ms/vs/17/release/vc_redist.x64.exe`, perguntado só o cabeçalho em 20/11/2026: leva a um arquivo
  cuja soma (no próprio endereço) é a do nosso `vc_redist.x64.exe` 14.44.35211.0.
