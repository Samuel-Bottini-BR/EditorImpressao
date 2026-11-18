# O motor do Kraken fora da atualização: como fazer (estudo, 18/11/2026)

Estudo do pesquisador para a decisão de hoje do Samuel ("mas dai vai ter que baixar o motor do kraken toda vez e
reinstalar ele de novo?" · "vou escolher a 16", D-768). **Nenhuma linha do programa nem dos testes mudou.** Nada
instalado, nenhuma janela na tela do Samuel, nenhuma pergunta do Windows. Ramo `kraken-separado-2026-11-18`.

Cada afirmação sobre o Velopack traz a linha do código lido (versão 1.2.161, `92d6a1c9`, licença MIT, cópia em
`saida_teste/publicar-rapido/fonte-velopack/`). O que é **conta** ou **não sei** está escrito assim.

## Em poucas frases

1. **Recomendação:** o motor mora numa pasta própria **ao lado** da pasta que a atualização troca, dentro da pasta do
   programa: `C:\Program Files\EditorImpressaoPrograma\motor-kraken\<versão do motor>\`. A atualização não toca nela
   (lido no código do Velopack) e o desinstalador do Velopack a apaga junto com o resto (lido no código). É o lugar que
   a própria documentação do Velopack manda usar para o que deve durar nas trocas e sair ao desinstalar.
2. **Como chega:** na primeira vez, dentro do instalador (.msi), como um arquivo só (o motor comprimido); o ajudante da
   atualização (a tarefa do Windows que já roda como o sistema) o põe no lugar, por trás, sem pergunta nova. Quando o
   motor mudar (raro), o mesmo ajudante baixa só o motor, assinado pelo Samuel, e **só troca o programa depois que o
   motor novo chegou inteiro**. Uma peça só faz as duas coisas.
3. **Tamanho e tempo depois:** a versão nova fica com **~460 MB** em vez de 826 MB (medido: soma das partes do pacote
   1.1.5 sem o motor) e **582 arquivos** em vez de 35.103. A troca no notebook deve cair de ~7,5 min para **uns 2 a 3
   min** (conta, a partir da proporção medida ao desempacotar; não medido no Velopack).
4. **Publicar** fica mais curto (uns **12 a 16 min**, contra 21 a 28 no plano de hoje; conta) e ocupa menos o C:.
5. **Quanto acrescenta ao plano da parte do Windows:** uns **12 a 18 h** de escrita (chute), mais 1 a 2 h para o agente
   que tenta quebrar, e uns **20 a 40 min a mais** de provas com o Samuel (as trocas mais curtas devolvem parte).
6. **Riscos maiores:** (a) para saber que motor a versão nova pede antes de trocar, o ajudante lê o pacote que o
   Velopack baixou, na pasta dele (lido no código, mas é um detalhe de dentro do Velopack); (b) "instalar por cima" com
   outro .msi: não sei o que o Velopack faz; (c) o espaço livre e o antivírus do notebook do Kaique não são conhecidos.
7. **Fato que o Samuel precisa saber:** hoje o Kraken **não é usado** no caminho do livro. A "segunda opinião" está
   desligada e sem tela (`core/linhas_do_texto.py:85`, `SEGUNDA_OPINIAO_DO_KRAKEN = False`; D-164 "pela metade"); só a
   conferência `--conferir-ocr` e o teste rápido da atualização o procuram. O motor vai ao Kaique porque ele decidiu
   "todos os OCRs instalados" (D-138). Por isso a prova de que o motor funciona é abri-lo e conversar com ele, não uma
   tela.
8. **Agora é o melhor momento:** nada do Velopack foi instalado ainda no notebook do Kaique. Depois da primeira
   instalação, mudar o lugar do motor exigiria código para mudá-lo de lugar em quem já tem.

---

## 1. Onde o motor fica, e quem cria a pasta

### O que o Velopack troca, apaga e deixa (lido no código)

- **Na troca de versão** ele renomeia a pasta `current` para uma temporária e põe a nova no lugar dela
  (`src/bins/src/commands/apply_windows_impl.rs:129-177`). Nada mais da pasta do programa é apagado: depois ele só
  atualiza o atalho, o `Update.exe` e o pequeno `.exe` de partida da raiz (linhas 208-270). Portanto **o que estiver ao
  lado de `current` sobrevive a toda troca**.
- Antes de trocar, ele fecha à força tudo o que roda **dentro da raiz** do programa (`apply_windows_impl.rs:159`;
  `src/bins/src/shared/util_windows.rs:81-98`). Um motor aberto em `raiz\motor-kraken` também é fechado. Isso já
  acontece hoje (o motor está em `current`) e é o que queremos: o programa está fechando.
- **As pastas temporárias** da troca ficam em `<raiz>\packages\VelopackTemp\` (`src/lib-rust/src/locator.rs:205-213`).
- **Ao baixar** uma versão, ele apaga os `*.nupkg` e `*.partial` velhos da pasta `packages`
  (`src/lib-rust/src/manager.rs:419-432`). Por isso o motor **nunca** pode morar em `packages`.
- **Ao desinstalar pelo .msi**, a ação de limpeza do Velopack apaga **a pasta de instalação inteira**, rodando como o
  sistema (`src/wix-dll/src/lib.rs:82-102`; no modelo do .msi, `Impersonate="no"` e condição de desinstalar,
  `src/vpk/Velopack.Packaging.Windows/Msi/Templates/MsiTemplate.hbs:197-199, 235`).
- **A documentação diz o mesmo:** "If you want to create settings that persist through updates, but are erased when
  the app is uninstalled, on Windows you should store them one level up (`..\`) outside of the `current` dir"
  (`docs/integrating/preserved-files.mdx`); e "Removes the entire install directory" ao desinstalar
  (`docs/integrating/uninstalling.mdx`).
- O caminho real da instalação, visto na etapa 5: `C:\Program Files\EditorImpressaoPrograma\` (com `current\` dentro)
  (`saida_teste/etapa5/registros/comparar-0-com-2.txt`).

### O lugar proposto

```
C:\Program Files\EditorImpressaoPrograma\
    current\                  <- o Velopack troca a cada versão (como hoje)
    packages\                 <- do Velopack
    Update.exe, Editor de Impressão.exe (o de partida)
    motor-kraken\             <- NOVO: o Velopack não toca; o desinstalador apaga
        1\                    <- uma pasta por versão do motor (python\, servidor_kraken.py, motor.json)
        .chegando-2\          <- só enquanto um motor novo está chegando (nunca com o nome final)
```

- **Uma pasta por versão do motor.** Assim nunca se troca um motor "por cima": o novo chega com outro nome, e o programa
  de cada versão procura exatamente a versão de motor que ele pede. A volta para a versão anterior (o socorro do plano)
  acha o motor dela ainda lá, sem internet. Ficam no máximo as duas versões mais novas; as outras são apagadas depois
  que a versão nova passou no teste rápido.
- **Licenças da pasta:** as que o Windows dá dentro de Arquivos de Programas (o sistema e os administradores mudam; as
  contas comuns só leem). **Nenhum comando de licença à mão** (a mesma regra da pasta segura do plano, peça 2).
- **Quem cria:** o **ajudante da atualização** (a tarefa que roda como o sistema, D-733), na primeira vez que ele roda
  depois do "Sim" da primeira abertura. Não é o gancho de instalar (roda sem administrador: achado B1, cabeçalho de
  `atualizacao.py`), nem a janela do Kaique (não tem licença para gravar em Arquivos de Programas). Não precisa de
  pergunta nova do Windows.

### Combinação com a "pasta segura" do plano

A pasta segura (peça 2 do plano) guarda o estado, o registro, os scripts e a cópia para voltar, e fica **fora** da raiz
do programa. O motor não vai para ela: ele é grande, tem versão, e pertence ao programa (sai sozinho ao desinstalar). Se
o Samuel preferir tudo fora da raiz, o motor pode ir para a pasta segura sem mudar o resto deste estudo; o custo é que
só a limpeza do desinstalar (peça 7) o tira, e não mais o próprio desinstalador. Ganho de brinde: a cópia para voltar
da pasta segura cai de ~788 MB para ~460 MB, porque o pacote fica sem o motor.

## 2. Como o motor chega

### 2.1 Na primeira instalação (D-727: tudo dentro do instalador)

- O instalador (.msi) da primeira entrega, e o que o Samuel pedir depois (D-777), leva o motor como **um arquivo só**,
  comprimido e assinado: `current\instalar\motor-kraken-<versão>.zip` (a mesma pasta `instalar\` onde já vai o Visual
  C++, `atualizacao.PASTA_DO_QUE_SE_INSTALA`). Nada é baixado ao instalar.
- Na primeira vez que o ajudante roda, ele vê que falta o motor que esta versão pede, acha o arquivo em `instalar\`,
  confere a assinatura, desempacota em `motor-kraken\.chegando-<v>\`, confere e só então dá o nome final. Roda por trás,
  como o sistema, com prioridade baixa (`atualizacao.xml_da_tarefa`, `atualizacao.py:1136-1142`: prioridade 7, limite de 2 h, "IgnoreNew"); **a janela do
  Kaique não espera nada**, porque nenhuma tela usa o Kraken hoje.
- Por que um arquivo só, e não os 34 mil soltos no .msi: assim a primeira instalação e a troca do motor usam **a mesma
  peça** (pôr no lugar um motor que veio num arquivo). Com os arquivos soltos seriam dois caminhos (mudar a pasta de
  lugar, e desempacotar o que veio da internet), e isso é o tipo de gambiarra do §11.12.
- **As versões de atualização não levam o motor** (nem o arquivo dele). Quem faz a diferença entre "atualização" e
  "instalador" é um lugar só do publicar (seção 5).
- O instalador e a atualização da mesma versão ficam com conteúdos diferentes (o instalador tem o arquivo do motor a
  mais). Isso não aparece para o Velopack: depois do .msi, a primeira atualização sempre vem pelo pacote inteiro
  (estudo de publicar, §2b: `create_delta_update_strategy`, "no local/base package available").

### 2.2 Quando o motor muda (raro)

- **Quanto muda:** o motor é o Python 3.12 com o Kraken 7.1.1 e o PyTorch, com 73 versões presas
  (`motor_kraken/requisitos-travados.txt`, memória `geral/ambiente.md`), mais o `servidor_kraken.py`. O protocolo está na
  versão 1 desde 29/09 (`core/ocr_kraken.py:97`). Muda quando o Samuel trocar o Kraken, o PyTorch ou o servidor
  (por exemplo na Fase 7, de transcrever).
- **A versão do motor tem um lugar só:** uma constante ao lado do `VERSAO_PROTOCOLO` em `core/ocr_kraken.py` (nome a
  escolher, ex. `VERSAO_DO_MOTOR`). O empacotador escreve, dentro de cada pacote do programa, um arquivo pequeno
  `motor-exigido.json` com essa versão, o nome do arquivo do motor e a soma dele.
- **Quem baixa e quando:** o mesmo ajudante, dentro de `procurar_e_preparar`, **depois de baixar a versão nova do
  programa e antes de trocar**:
  1. confere a assinatura da versão nova (como hoje, D-724) e baixa;
  2. abre o pacote baixado, confere a soma dele contra a assinada (o próprio programa, não só o Velopack) e lê o
     `motor-exigido.json` de dentro;
  3. se esse motor já está instalado e confere: segue para a troca, como hoje (**nada do motor é baixado**);
  4. se não: baixa o motor do GitHub (uma publicação própria, etiqueta `motor-kraken-<v>`), confere a soma e a
     assinatura, põe no lugar (como em 2.1) e só então segue para a troca.
- **Onde o Velopack deixa o pacote baixado** (para o passo 2): `<raiz>\packages\<id>-<versão>-full.nupkg` quando a raiz
  aceita gravação, que é o caso do ajudante, que roda como o sistema (`locator.rs:153-159`, `manager.rs:408-412`).
  É um detalhe de dentro do Velopack, documentado só como "PackagesDir" (`preserved-files.mdx`). Se um dia mudar, o
  programa não acha o pacote e **não troca** (registra e tenta depois): falha segura, nunca troca sem motor.
- **A publicação do motor no GitHub não atrapalha o Velopack:** ele procura versões só nas publicações que têm o
  arquivo `releases.win.json` e pula as outras (`src/lib-rust/src/sources/mod.rs:112-144`). Ele lê só as 10
  publicações mais novas (`sources/github.rs:80`); a do motor ocupa um desses lugares enquanto for nova. Não atrapalha a
  volta, que baixa pelo endereço direto (`atualizacao.voltar_para_a_anterior`).

### 2.3 A assinatura (D-724)

- O motor é assinado com a **mesma chave** do Samuel e conferido pela **mesma peça** (`assinatura.py`), sem mudar nada
  nela: o arquivo de assinatura já diz o "pacote", a versão, o nome do arquivo e a soma (`assinatura.VersaoAssinada`,
  `assinatura.py:211-218`), e a conferência recusa assinatura de outro pacote (`conferir_versao`, `assinatura.py:285-286`).
  O motor usa outro nome de pacote (ex. `EditorImpressaoMotorKraken`, ao lado do `ID_DO_PACOTE` em `versao.py`). Uma
  assinatura do motor nunca vale como assinatura do programa, nem o contrário.
- A soma do motor também vai dentro do pacote do programa (o `motor-exigido.json`), que já é coberto pela assinatura do
  programa. São duas travas: a versão nova só aceita **aquele** motor, e o motor só entra com a assinatura do Samuel.
- O arquivo do motor dentro do .msi também é conferido pela assinatura antes de ir para o lugar.

### 2.4 Tudo ou nada

- O motor novo nunca aparece com o nome final pela metade: ele chega em `.chegando-<v>`, é conferido, e só um
  renomear (no mesmo disco, de uma vez só) dá o nome final.
- **O programa continua com o motor velho** até o novo estar inteiro, e a versão nova do programa **espera** o motor
  (pergunta 3 para o Samuel). Se o motor não chega (internet caiu), o Kaique fica na versão de hoje, que funciona, e o
  ajudante tenta de novo na próxima abertura, sem aviso (falha passageira, como no plano, peça 4).

## 3. Como o programa acha o motor e confere que ele está inteiro

- **A regra de achar continua num lugar só:** `core/ocr_kraken.lugares_do_motor()` (hoje: ao lado do `.exe`, na raiz do
  código, e na pasta das ferramentas, `core/ocr_kraken.py:129-144`). Passa a ser: no programa instalado pelo Velopack,
  só `<raiz>\motor-kraken\<versão que este programa pede>\`; no portátil e pelo código, os lugares de hoje.
- **Uma conferência só** ("está inteiro e é da versão certa"), usada por todos: o motor (`MotorKraken`), o teste rápido
  da atualização (hoje procura `motor-kraken/python/python.exe` ao lado do `.exe`, `atualizacao.py:616-621`), a
  conferência `--conferir-ocr`, o ajudante (antes e depois de pôr no lugar) e o empacotador (que hoje tem a sua
  própria, `empacotar.conferir_motor_kraken`). Ela lê o `motor.json` que vai dentro do motor (versão do motor, versão do
  protocolo, e a lista de arquivos com o tamanho de cada um) e confere a versão e que cada arquivo está lá com o
  tamanho certo. Medido: listar e medir os 34.521 arquivos leva **2,9 s** com o disco já lido uma vez (HD do D:); a
  primeira leitura, com o disco frio, levou bem mais (não cronometrado).
- **A conferência forte é na chegada:** a soma do arquivo do motor (assinada) e a conferência de cada arquivo que o
  próprio Python faz ao desempacotar (ele recusa um arquivo com a soma interna errada: "Bad CRC-32",
  `Lib/zipfile/__init__.py:1115` do Python 3.14). Por isso não é preciso somar os 1,1 GB arquivo por arquivo depois:
  medido no HD do D:, essa soma passou de 5 minutos e eu a interrompi; no disco de dentro não foi medida.
- **A prova de que funciona é o próprio motor responder:** abrir o motor já confere a versão do protocolo
  (`core/ocr_kraken.py:280-285`). O teste rápido depois de uma troca passa a abrir o motor de verdade e esperar o
  "pronto", e não só ver que o arquivo existe (D-767: nada de "deu certo" sem prova). Custo: a primeira abertura do motor
  depois de instalar levou 52 a 65 s no PC do Samuel (memória `itens/6.8.md`, antivírus lendo arquivos novos); as
  seguintes, 6 a 7 s.
- **O que aparece na tela se o motor faltar ou estiver estragado:** hoje, **nada** para o Kaique, porque nenhuma tela
  usa o Kraken; o motivo vai para o registro, que a gerente lê de longe (D-719). O ajudante vê a falta na próxima vez
  que roda e põe o motor de novo (baixando, se o arquivo do instalador já saiu). Quando o Kraken ganhar tela (Fase 1.5),
  aparece o aviso que já existe, "O detector de linhas do Kraken não está instalado [...] As outras funções continuam
  funcionando." (`core/ocr_kraken.py:113-114`). O aviso de versão diferente diz "É preciso reinstalar o programa."
  (`core/ocr_kraken.py:121-122`), o que deixa de ser verdade: é texto de tela, e muda só com o "sim" dele quando a tela
  existir.

## 4. Falhas, desinstalar e reinstalar

### 4.1 O que pode dar errado ao pôr o motor no lugar, e o que o programa faz

| Caso | O que o programa faz | O Kaique vê |
|---|---|---|
| Sem internet, ou a internet cai no meio do download do motor | apaga o pedaço baixado; não troca o programa; tenta na próxima abertura | nada (falha passageira) |
| A soma ou a assinatura do motor não confere | recusa a versão nova (registrar_falha "recusada"); motor e programa de hoje ficam | o aviso de assinatura (a frase 2 da D-778), uma vez |
| Disco cheio (confere o espaço antes: o arquivo e o motor aberto, uns 1,5 GB; mais 1,1 GB se o velho ainda estiver lá) | não começa, ou apaga o que fez nesta vez; tenta depois | nada; o registro diz "falta espaço" |
| Notebook desligado no meio | sobra só a pasta `.chegando-<v>`, nunca com o nome final; a próxima vez a apaga e recomeça | nada |
| O antivírus tira ou segura um arquivo do motor | o desempacotar ou a conferência acusa; apaga e tenta de novo na próxima vez | nada; o registro diz qual arquivo |
| O motor instalado se estraga depois | a conferência acusa no uso ou no ajudante; o ajudante põe de novo | nada hoje (sem tela) |
| "Não" na pergunta do Windows da primeira abertura | sem ajudante, o motor não vai para o lugar; o arquivo fica em `instalar\`; a pergunta volta (D-741) | o mesmo de hoje ("Nada mudou") |
| A versão nova pede um motor que não foi publicado | o publicar recusa liberar a versão sem o motor publicado e lido de volta (seção 5); no Kaique, seria tratado como falha passageira | nada |
| A volta para a versão anterior | o motor dela continua na pasta dela; volta sem internet | o aviso da volta (D-778, frase 1) |
| Dois ajudantes ao mesmo tempo | a tarefa já não deixa ("IgnoreNew", `atualizacao.xml_da_tarefa`) | nada |
| O Kaique abre o programa enquanto o motor chega | sem problema: o motor novo ainda não tem o nome final | nada |

Ponto a amarrar no plano: com "IgnoreNew", um "Reiniciar agora" no meio de um ajudante que está pondo o motor no lugar
não abre um segundo ajudante. O "sinal de fim" do plano (peça 4) tem de esperar o ajudante que já está rodando.

### 4.2 Desinstalar (D-731, D-764)

- **Desinstalar tira o motor:** a pasta `motor-kraken\` está dentro da pasta de instalação, que a limpeza do .msi apaga
  inteira, como o sistema (`src/wix-dll/src/lib.rs:98-102`). Os projetos do Kaique ficam em `%LOCALAPPDATA%\EditorImpressao`,
  fora do alcance (D-763).
- **Cuidado:** a limpeza do Velopack ignora os erros (`MsiTemplate.hbs:199`, `Return="ignore"`; `lib.rs:100`, só anota).
  Se o motor estiver aberto (o programa aberto durante o desinstalar), um arquivo preso pode sobrar. O motor fecha
  sozinho quando o programa fecha (`core/ocr_kraken.py:192`). A limpeza do desinstalar do plano (peça 7) passa a
  conferir também que `motor-kraken\` saiu e apaga o que sobrou.

### 4.3 Reinstalar

- Como o desinstalar apaga o motor, **reinstalar traz o motor de novo pelo instalador** (que o leva dentro, D-777),
  sem baixar nada. Não há reaproveitamento, e não precisa.
- **"Instalar por cima"** (rodar outro .msi com o programa ainda instalado): o modelo do .msi do Velopack 1.2.161 não tem
  regra de atualização maior (`MajorUpgrade`; procurei em `MsiTemplate.hbs` e não achei). **Não sei** o que o Windows faz
  nesse caso (pode recusar, instalar ao lado ou apagar a pasta). Já é uma dúvida do plano hoje (risco 4); o motor não
  muda a resposta, só o tamanho do que se perde se a pasta for apagada (ele volta pelo próprio .msi).
- Se um dia trocar para o Velopack 1.3 (D-779), as mudanças dele na limpeza do .msi ("stop wiping user data on MSI
  upgrades", estudo de publicar §3.6) têm de ser relidas para o motor também.

## 5. Publicar

### Versão nova do programa (a de toda hora)

| | Hoje (pacote com o motor) | Sem o motor | Fonte |
|---|---|---|---|
| Arquivos no pacote | 35.103 | 582 | medido no pacote 1.1.5 |
| Tamanho, aberto | 2.011 MB | 868 MB | medido (soma das entradas) |
| Tamanho, comprimido (o que o Kaique baixa) | 826 MB | ~460 MB | medido (soma das entradas comprimidas) |
| Montar a pasta do programa | 10 min 16 s (D:) | uns 6 a 8 min | medido / conta (tira a cópia dos 34 mil arquivos) |
| O Velopack empacotar, no C: | 7 min 39 s (M2b) | uns 3 a 4 min | medido / conta (a compressão é proporcional aos bytes) |
| Enviar | ~1,7 GB | ~0,9 GB (o pacote e o Setup.exe, que leva o pacote dentro) | conta |
| **Total** | **21 a 28 min** (plano de hoje) | **uns 12 a 16 min** | conta |
| Pico de espaço no C: | 5,3 a 6,1 GB | uns 2,5 a 3 GB | medido / conta |

Com a reserva de 20 GB livres no C: (D-776) e os 40 GB livres de hoje, sobra folga nos dois casos.

### O que muda no publicar e no empacotar

- **As três saídas num lugar só** do empacotador, em vez de cópias: (1) a **pasta portátil** (`--modo pasta`), com o
  motor solto ao lado do `.exe`, como hoje; (2) a **atualização**, sem o motor, com o `motor-exigido.json`; (3) o
  **instalador**, que é a atualização mais o arquivo do motor em `instalar\` e o `--msi` (D-777).
- **Antes de liberar uma versão**, o publicar confere que o motor que ela pede está publicado no GitHub e o lê de volta
  (a mesma regra "nunca pela metade" do plano, peça 8).
- **Montar uma versão nova do motor** (raro): `montar_motor_kraken.py` como hoje, mais o `motor.json`; depois um passo
  novo do publicar comprime o motor, assina e publica na etiqueta `motor-kraken-<v>`. Tempo: comprimir os 34.521
  arquivos no C: uns 3 a 5 min (conta, pela velocidade medida no estudo de publicar); assinar, uns segundos; enviar
  357 MB. O tempo do `montar_motor_kraken.py` (que baixa e confere cada peça) não foi medido hoje. O limite do GitHub
  para um arquivo publicado é de 2 GB (documentação do GitHub, que eu não reli hoje).
- **O instalador sob pedido** (D-777): o tempo do .msi com o motor dentro como um arquivo só **não foi medido** (hoje,
  com os 35 mil arquivos soltos, leva de 33 a 43 min no D:).
- Duas listas que hoje se repetem ficam numa só: `empacotar.LUGARES_DO_MOTOR` (onde achar o motor **para montar**) e
  `core/ocr_kraken.lugares_do_motor` (onde o programa o procura) são coisas diferentes e devem ter nomes que digam isso;
  a conferência do motor passa a ser uma só (seção 3). Já é o item 57 da lista do plano.

## 6. Os portáteis, o atalho "(desenvolvimento)" e os testes

- **Atalho "(desenvolvimento)":** roda pelo código (`main.py` na pasta principal); o motor continua achado na pasta das
  ferramentas (`D:\programas\EditorImpressao-arquivos\ferramentas\motor-kraken\`, que existe hoje: 34.521 arquivos,
  1.143 MB, medido). Nada muda.
- **A pasta portátil** (`empacotar.py --modo pasta`): continua com o motor solto ao lado do `.exe`, e o programa o acha
  ali como hoje. O zip portátil do Velopack já deixou de sair (D-777). O arquivo único do pendrive nunca levou o Kraken
  (cabeçalho de `empacotar.py`).
- **Os testes:** pela busca nos testes (`motor-kraken`, `PASTA_DO_MOTOR`, `AMOSTRA_DO_MOTOR`, `lugares_do_motor`),
  **nenhum teste antigo cobra o motor dentro do pacote do Velopack**. O teste do Visual C++ no pacote monta a lista com a
  própria função (`tests/test_decisoes_atualizacao.py:537-557`), e continua valendo. Os testes do Inno
  (`tests/test_empacotar.py`) cobram o Inno, que continua até o Samuel decidir tirá-lo. Os testes com o motor de verdade
  (`tests/test_ocr_kraken.py`) continuam achando-o pelos lugares do código. Continua o defeito antigo de, numa cópia do
  projeto, o motor não ser achado e os testes pularem calados (Lista de bugs, nº 330); este estudo não o resolve.
- **Testes novos:** a lógica (que lugar, que versão, o `motor.json`, a ordem "motor antes da troca", cada linha da tabela
  4.1) com pastas de mentira; mas, pela D-767, **o que vale é a prova à vista** (seção 7).

## 7. O que muda no plano da parte do Windows

### Peças

- **Peça 4 (a troca):** um passo novo dentro de `procurar_e_preparar`, "garantir o motor que a versão nova pede"
  (seção 2.2), e o teste rápido passa a abrir o motor (seção 3). O socorro guarda um pacote menor (~460 MB).
- **Peça nova, "o motor no lugar":** uma peça só que acha, confere e põe o motor no lugar, vindo do instalador ou da
  internet. É chamada em dois lugares: no começo de cada rodada do ajudante (a primeira instalação e o conserto
  sozinho) e antes da troca (o motor novo).
- **Peça 7 (desinstalar):** confere também que o motor saiu.
- **Peça 8 (publicar):** as três saídas, o `motor-exigido.json`, o passo de publicar o motor e a conferência antes de
  liberar.
- **Peças 1, 2, 3, 5 e 6:** não mudam.
- **A decisão 1 do plano (versão inteira ou só a diferença)** volta para o Samuel com os números novos (pergunta 2): sem
  o motor, a versão inteira fica com ~460 MB.
- **A decisão 16 do plano ("para depois")** deixa de existir: virou a D-768.

### Provas à vista (D-767, D-773, D-775)

- **Sessão B (o atualizador):** instalar pelo .msi; depois do "Sim", a janela de prova mostra a pasta
  `motor-kraken\1\` nascendo e a conferência "motor 1, inteiro"; uma versão nova **sem** troca de motor chega sem baixar
  o motor (o registro e a data da pasta provam); uma versão que pede o **motor 2**: o motor chega, o programa troca, o
  teste rápido abre o motor 2; um **motor 2 com assinatura falsa**: recusado com o aviso certo, tudo fica como estava;
  **fechar a janela que serve as versões no meio do download do motor**: nada muda, e ao reabrir chega; **a versão que
  nem abre** volta para a anterior, que acha o motor dela sem internet. Uns 45 a 60 min a mais (chute), com umas 4 a 5
  trocas mais curtas devolvendo uns 20 min (conta). Nenhuma pergunta do Windows a mais.
- **Sessão C:** depois do desinstalar, a janela de prova lista que `motor-kraken\` saiu; depois do reinstalar, que o
  motor voltou sem baixar. Uns 5 a 10 min a mais.
- **Versões de prova a montar:** mais um motor 2 de verdade (pode ser o mesmo motor com outra versão escrita) e um motor
  com assinatura falsa; cada versão do programa fica mais rápida de montar. Mais ou menos o mesmo tempo de hoje (conta).

### Tempo que acrescenta

- **Escrever (chute; nada parecido foi medido):** a peça de achar e conferir, com o `motor.json` no montar: 2 a 3 h; a
  peça de pôr no lugar, com a lista de falhas da seção 4.1 e a ligação ao ajudante: 5 a 7 h; empacotar e publicar: 3 a
  5 h; testes da lógica: 2 a 3 h. **Total: 12 a 18 h**, sobre as 27 a 40 h do plano.
- **Tentar quebrar (D-775):** 1 a 2 h a mais.
- **Provas com o Samuel:** uns **20 a 40 min a mais** no total.

### Riscos novos

1. **Ler o pacote baixado na pasta do Velopack** (seção 2.2): é detalhe de dentro dele. Falha segura se mudar, mas
   precisa ser relido a cada troca de versão do Velopack.
2. **Espaço no notebook do Kaique:** não se sabe quanto há livre. A troca do motor precisa de uns 2,6 GB por um tempo
   (o arquivo, o novo e o velho).
3. **Antivírus do Kaique** lendo 34 mil arquivos novos na primeira vez: pode deixar essa primeira rodada do ajudante bem
   mais lenta (não medido lá), e pode tirar algum arquivo do motor.
4. **"Instalar por cima" com outro .msi**: não sei o que acontece (seção 4.3).
5. **O instalador e a atualização da mesma versão com conteúdos diferentes** (o arquivo do motor a mais): é preciso que
   isso esteja escrito num lugar só do publicar, ou um agente vai achar que é defeito.
6. **A publicação do motor no GitHub** ocupa um dos 10 lugares que o Velopack lê (seção 2.2): não atrapalha hoje, mas
   precisa ser lembrado se um dia a "diferença" voltar.
7. **O ajudante fica ocupado mais tempo** na rodada em que o motor chega (seção 4.1, "IgnoreNew").

## 8. As alternativas

| Alternativa | O que é | Limpa ou remendo | Recomendo? |
|---|---|---|---|
| **A. Pasta do motor ao lado de `current`, posta pelo nosso ajudante** (seções 1 a 7) | uma peça só para a primeira vez e para o motor novo; o lugar que o Velopack documenta; o desinstalador do Velopack já apaga | **limpa** | **sim** |
| A'. A mesma coisa, mas na pasta segura do plano (fora da raiz) | igual à A; só o desinstalar muda: quem tira é a nossa limpeza (peça 7), não o Velopack | limpa | segunda opção |
| B. Um segundo pacote do Velopack só para o motor (outro nome interno) | o Velopack trata o motor como outro programa: ele precisa de um `.exe` principal, ganha a sua própria entrada na lista de programas do Windows e o seu próprio desinstalar (a limpeza de um .msi só apaga a pasta dele, `lib.rs:98`); o ajudante teria de atualizar dois programas; os dois no mesmo GitHub: não li como o Velopack separa as versões de dois pacotes no mesmo lugar (não sei) | **remendo**: usa uma ferramenta de atualizar programas para guardar uma pasta de arquivos, e deixa dois programas para o Kaique | não |
| C. Algum recurso do próprio Velopack | **não existe** na 1.2.161 um jeito de "peça instalada uma vez": o único recurso de dependências é uma lista fixa de peças da Microsoft (Visual C++, .NET, WebView2), baixadas da internet na hora (`src/bins/src/windows/runtimes.rs:45-73`, `prerequisite.rs:43-56`), o que também iria contra a D-727. A "diferença" não resolve: mesmo baixando pouco, ele remonta e desempacota o motor inteiro a cada troca (estudo de publicar, §2b). O que o Velopack oferece é a regra "guarde um nível acima de `current`", que é a alternativa A | — | (é a A) |
| D. O motor como um arquivo só dentro de **todo** pacote, desempacotado só quando muda | a troca fica rápida (poucos arquivos), mas o Kaique baixa os 357 MB do motor em toda versão | **remendo** frente à decisão dele ("só é baixado de novo se ele mesmo mudar") | não |
| E. Um instalador à parte só para o motor | o Kaique rodaria dois instaladores; o Inno sai (D-723) | remendo | não |

Nenhuma alternativa exige outra versão do Velopack (D-779 continua valendo).

## 9. Perguntas para o Samuel

(No formato do CLAUDE.md §11.13. A gerente confere a lista antes de publicar. Não há print possível: tudo acontece por
trás, sem janela. Pode ir um desenho simples das pastas, dizendo que é desenho.)

### Pergunta 1. Onde fica o motor do Kraken e como ele chega

- **Do que se trata.** É a peça do programa que acha as linhas de texto (o "Kraken"). Tem 1 GB e 34 mil arquivos, quase
  todos os arquivos do programa. Fica dentro da pasta do programa, em Arquivos de Programas.
- **O que acontece hoje.** Ela vai inteira em toda versão nova, e o notebook do Kaique a desmonta e monta de novo a cada
  troca. É por isso que a troca leva uns 7 minutos e meio.
- **O que você escolhe:**
  - **Uma pasta própria do motor, junto do programa (sugestão).** A atualização não mexe nela. Na primeira vez ela vem
    dentro do instalador. Quando o motor mudar (raro), o programa baixa só ele, com a sua assinatura. Desinstalar tira
    junto. A versão nova fica com uns 460 MB, e a troca com uns 2 a 3 minutos (conta, não medida). Nada muda na tela
    nem no livro.
  - **Um segundo programa só para o motor.** O Windows mostra dois programas na lista ("Editor de Impressão" e "Motor
    do Kraken"), e desinstalar um não tira o outro sozinho. Não recomendo.
  - **Só comentário.**
- **De onde veio.** Pedido seu de hoje. A ferramenta de atualização não tem um jeito próprio para isso; a documentação
  dela manda guardar o que deve durar numa pasta ao lado da do programa, que é a sugestão.
- **Bom saber.** Hoje o Kraken ainda não é usado em nenhuma tela: a "segunda opinião" dele está desligada. Ele vai ao
  Kaique porque você decidiu, em 29/09, "todos os OCRs instalados".
- **Situação.** Só estudo; nada escrito. Acrescenta ao plano uns 12 a 18 horas de trabalho de agente e uns 20 a 40
  minutos nas provas com você.

### Pergunta 2. A versão inteira ou só o que mudou, agora sem o motor

- **Do que se trata.** É a atualização que chega sozinha no notebook do Kaique quando ele abre o programa. Hoje de manhã
  você deixou essa escolha para depois deste estudo.
- **O que acontece hoje.** Ele baixa só o que mudou (uns 20 MB), mas o notebook remonta a versão inteira antes de trocar
  (22 minutos no seu PC). E por esse caminho a sua assinatura não confere tudo.
- **O que você escolhe:**
  - **A versão inteira (sugestão).** Sem o motor, ela fica com uns 460 MB: uns 1 minuto e meio a 50 Mbps, uns 6
    minutos a 10 Mbps (conta). A troca fica em uns 2 a 3 minutos. A assinatura confere tudo.
  - **Só o que mudou.** Baixa uns 20 MB, mas o notebook ainda remonta a versão (uns 5 a 7 minutos a mais; conta). E a
    assinatura precisa passar a conferir a diferença também (mudança no programa).
  - **Só comentário.** Se souber, diga a velocidade da internet do Kaique.
- **Situação.** Aberta desde hoje de manhã; o resto do plano não depende dela.

### Pergunta 3. Quando o motor muda, a versão nova espera ele chegar?

- **Do que se trata.** É o caso raro em que uma versão nova do programa precisa de um motor novo.
- **O que você escolhe:**
  - **Sim, tudo ou nada (sugestão).** A versão nova só entra depois que o motor novo chegou inteiro e conferido. Se a
    internet cair, o Kaique continua na versão de antes, com o motor de antes, e o programa tenta de novo na próxima
    abertura. É o mesmo jeito que você escolheu para os testes à distância.
  - **Não.** A versão nova entra logo e o motor chega depois; nesse meio-tempo, o Kraken não funciona.
  - **Só comentário.**
- **Situação.** Só estudo. Nada do que já funciona muda.

## 10. Medidas e fontes

### Medidas desta tarefa (18/11/2026, PC do Samuel, só no D:)

| Medida | Resultado |
|---|---|
| Motor das ferramentas (`EditorImpressao-arquivos\ferramentas\motor-kraken`): arquivos e bytes | 34.521 arquivos, 1.143.431.232 bytes; listar e medir: 2,9 s (com o disco já lido) |
| Somar cada arquivo do motor (SHA-256), lendo do HD | passou de 300 s e foi interrompida (o disco estava frio) |
| Pacote 1.1.5 (`saida_teste/etapa5/servidor/`): entradas | 35.103; motor 34.521 (1.143 MB aberto, 357 MB comprimido); resto 582 (868 MB aberto, 460 MB comprimido) |
| Desempacotar o resto (582 arquivos) no D:, com o Python | 42,8 s |
| Desempacotar 3.000 arquivos do motor (85 MB) no D:, com o Python | 9,4 s (conta: o motor inteiro, uns 110 a 125 s; o motor é uns 70 a 75% do tempo de desempacotar) |

A pasta da medida (`saida_teste/kraken-separado/medida-extrair`, 916 MB, só minha) foi apagada no fim. Nada foi gravado
no C: além de dois scripts pequenos na pasta de rascunho da sessão.

### O que não foi medido nem lido

- A troca de verdade pelo Velopack sem o motor (só a conta da tabela acima).
- O .msi com o motor dentro como um arquivo só.
- Desempacotar o motor no disco de dentro (SSD) e no notebook do Kaique.
- O que o Windows faz ao "instalar por cima" com o .msi do Velopack.
- Como o Velopack separa dois pacotes de nomes diferentes no mesmo GitHub (só para a alternativa B).
- O espaço livre e o antivírus do notebook do Kaique.

### Fontes lidas

- Velopack 1.2.161 (`92d6a1c9`, MIT): `src/bins/src/commands/apply_windows_impl.rs`, `uninstall.rs`,
  `src/bins/src/shared/util_windows.rs`, `src/bins/src/windows/runtimes.rs`, `prerequisite.rs`,
  `src/lib-rust/src/locator.rs`, `manager.rs`, `sources/github.rs`, `sources/mod.rs`, `src/wix-dll/src/lib.rs`,
  `src/vpk/Velopack.Packaging.Windows/Msi/Templates/MsiTemplate.hbs`, `Msi/MsiBuilder.cs`.
- Documentação do Velopack (cópia local, `fonte-velopack/docs/repo/docs/`): `integrating/preserved-files.mdx`,
  `integrating/uninstalling.mdx`, `packaging/operating-systems/windows.mdx`.
- Python 3.14: `Lib/zipfile/__init__.py:1115` (a conferência de cada arquivo ao desempacotar).
- Nosso código (só lido): `core/ocr_kraken.py`, `core/linhas_do_texto.py`, `core/ocr_diagnostico.py`, `atualizacao.py`,
  `empacotar.py`, `publicar_versao_kaique.py`, `assinatura.py`, `versao.py`, `tests/test_empacotar.py`,
  `tests/test_decisoes_atualizacao.py`, `tests/test_ocr_kraken.py`.
- O plano da parte do Windows (ramo `plano-windows-2026-11-18`), o estudo de publicar mais rápido (ramo
  `publicar-rapido-2026-11-18`), o Livro (D-138 a D-140, D-164, D-723 a D-783), a memória (`itens/6.8.md`,
  `itens/1.3.md`, `geral/ambiente.md`) e o registro da etapa 5 (`saida_teste/etapa5/registros/comparar-0-com-2.txt`).

### Licenças

| O que é | Licença | Roda aqui? | No notebook do Kaique? |
|---|---|---|---|
| Velopack 1.2.161 | MIT | sim (etapa 5) | sim (já vai no programa) |
| Kraken 7.1.1 (dentro do motor) | Apache-2.0 (pela página do projeto; não reli hoje) | sim, no motor à parte | sim, no motor à parte |
| PyTorch (dentro do motor) | BSD-3 (não reli hoje) | sim | sim |
| Python 3.12 embutível (dentro do motor) | PSF | sim | sim |
