# Prova à vista do atualizador: o roteiro

Preparado em 25/11/2026 para a prova no PC do Samuel. **Nada disto foi feito ainda na tela dele**: é o plano, passo a
passo. A gerente pilota; o Samuel olha e clica "Sim" ou "Não" quando a gerente pedir.

## Para o Samuel: o que vai acontecer

**O que é.** É o teste do jeito novo de o Editor de Impressão se atualizar sozinho pela internet, feito no seu
computador, com o programa instalado de verdade (como o Kaique vai ter). As versões novas vêm de uma pasta do seu
computador que faz o papel da internet. Elas são versões de verdade do programa, montadas hoje, com números de prova
(1.9.0 a 1.9.6), e nunca vão ao GitHub nem ao Kaique.

**O que você faz.** Olha a tela e clica onde a gerente pedir. Nas perguntas do Windows ("Deseja permitir que este
aplicativo faça alterações no seu dispositivo?"), a gerente diz antes se é "Sim" ou "Não". Dessas perguntas, a foto é
do seu celular: o Windows não deixa tirar print delas.

**Quantas perguntas do Windows: 5 durante a prova** (passo 0: 1; passo 1: 3; passo 11: 1), **e mais 1 depois**, na
limpeza, se você disser que pode apagar o que sobrou. Do passo 2 ao 10, nenhuma: é o que a prova quer mostrar.

**Quanto tempo: de 1h30 a 2h.** A instalação leva uns 3 minutos; cada troca de versão, de 1 a 3 minutos.

**Seus projetos.** A pasta dos seus projetos não é apagada nem mexida pela prova: a gerente tira uma "foto" dela antes
e confere depois. O programa instalado usa a mesma pasta de dados do seu atalho de sempre, como sempre: ele grava ali o
que grava ao abrir e fechar (as configurações, a lista de avisos já vistos).

**Duas coisas que você vai ver e que já estão decididas para depois da entrega** (você decidiu hoje, 25/11, que ficam
para depois):
- na versão quebrada de propósito (passo 4), depois da caixa certa aparece também a caixa de sempre do programa, "Um
  momento — Aconteceu um problema inesperado, mas o programa continua funcionando.", e o programa fecha. Essa frase não
  é verdade nesse caso; está na lista de depois;
- a janelinha da troca é a do próprio Velopack (o texto é dele), como você decidiu em 23/11.

**Uma coisa que não aparece nesta prova:** a janela da senha dos testes à distância. Ela só aparece uma vez por conta
do Windows, e a sua conta já a viu em 22/11. No notebook do Kaique ela aparece uma vez, e ele clica "Agora não".

## Um passo do plano que não dá para fazer como estava escrito

**O passo 6 do plano** ("fechar a janela das versões no meio do download") **não dá para fazer com o programa de
hoje.** O plano de 18/11 dizia que as versões viriam de uma janelinha visível, que faz o papel da internet, e que
fechá-la no meio do download seria "a internet caindo". O programa novo só sabe ler as versões de prova de uma
**pasta** (não de uma janela): de uma pasta, o download é uma cópia de segundos, e não há o que fechar no meio.
**No lugar dele**, o roteiro traz o passo 6 de outro jeito: a pasta das versões "para de responder" (como sem
internet), com e sem a versão nova já baixada. A pergunta sobre isso está no fim ("Perguntas para você").

## Como cada passo está escrito

Cada passo diz: **para que serve**; **a gerente faz** (os comandos, já escritos); **você clica**; **tem que aparecer**
(as palavras exatas combinadas com você); **conferido por fora** (o que a gerente lê no disco e no Windows, sem mudar
nada); **o print**. O número da decisão vai no fim, entre parênteses, só para consulta.

Os comandos da gerente usam sempre os caminhos inteiros (nada depende de uma variável de antes). Os quatro que mais se
repetem:

- **conferir por fora**: `& "D:\programas\EditorImpressao\.venv\Scripts\python.exe" "D:\programas\EditorImpressao\.claude\worktrees\atualizador-novo\relatorios\atualizador-novo\prova-a-vista\conferir_instalacao.py"`
- **publicar uma versão** (passa do "estoque" para a pasta das versões publicadas): `& "D:\programas\EditorImpressao\.venv\Scripts\python.exe" "D:\programas\EditorImpressao\.claude\worktrees\atualizador-novo\relatorios\atualizador-novo\prova-a-vista\fonte_da_prova.py" liberar 1.9.1`
- **pôr de lado / de volta**: `... por_de_lado.py <comando>` (mesmo começo)
- **print**: `... tirar_print.py <nome>` (mesmo começo)

Abaixo, `PY` quer dizer `& "D:\programas\EditorImpressao\.venv\Scripts\python.exe"` e `P\` quer dizer a pasta
`D:\programas\EditorImpressao\.claude\worktrees\atualizador-novo\relatorios\atualizador-novo\prova-a-vista\`.

---

## Passo 0 — Antes de começar (5 min; 1 pergunta do Windows)

**Para que serve:** conferir que o computador está limpo, ligar a vigia (que anota a hora de cada janela, para as
medidas) e criar o arquivo que aponta o programa para a pasta das versões de prova.

**A gerente faz:**
1. `PY P\conferir_instalacao.py` → tem de dizer "não está instalado", "nenhuma entrada Editor de Impressão" e
   "fonte-de-teste.txt: não existe".
2. `PY P\fonte_da_prova.py estado` → "servida: v1.9.0" (só ela) e "a fonte oferece: 1.9.0".
3. `PY P\projetos_antes_e_depois.py tirar antes` (a foto da sua pasta de projetos).
4. A vigia, por trás (a ferramenta com "rodar por trás"): `PY P\vigiar_janelas.py 10800`.
5. O arquivo da fonte de teste, com licença (é aqui a pergunta do Windows):
   `Start-Process powershell.exe -Verb RunAs -Wait -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','D:\programas\EditorImpressao\.claude\worktrees\atualizador-novo\relatorios\atualizador-novo\prova-a-vista\criar_fonte_de_teste.ps1'`
6. `PY P\conferir_instalacao.py` de novo.

**Você clica:** "Sim" na pergunta do Windows (ela diz "Windows PowerShell"). Uma janela azul do PowerShell aparece e
some sozinha.

**Tem que aparecer:** nada no programa (ele ainda não está instalado).

**Conferido por fora:** o passo 6 diz `fonte-de-teste.txt: "C:\EditorImpressaoProva\prova-a-vista-25-11\fonte"; dono
S-1-5-32-544`. O registro `C:\EditorImpressaoProva\prova-a-vista-25-11\registros\criar_fonte_de_teste.txt` diz
"confere: True". Se o dono não for S-1-5-32-544, **parar**: o programa ignoraria o arquivo e procuraria no GitHub.

**Print:** foto do celular da pergunta do Windows (`p00-pergunta-powershell`).

---

## Passo 1 — Instalar e abrir pela primeira vez (10 min; 3 perguntas do Windows)

**Para que serve:** ver a instalação de verdade e a primeira abertura: a pergunta do Windows vem logo depois do clique
no atalho, antes da janela; com "Não", o programa abre e a pergunta volta da próxima vez; com "Sim", ela nunca mais
aparece.

**A gerente faz:**
1. Abre o instalador (como um clique duplo, sem licença): `Start-Process "C:\EditorImpressaoProva\prova-a-vista-25-11\servida\v1.9.0\EditorImpressaoPrograma-1.9.0-win.msi"`
2. Depois do "Não" (abaixo): `PY P\conferir_instalacao.py`.
3. Depois do "Sim": espera 2 minutos (o motor de achar texto é posto no lugar, por trás) e `PY P\conferir_instalacao.py`.

**Você clica:**
1. No instalador: os botões de seguir até "Instalar"; "Sim" na pergunta do Windows (a 1ª deste passo). **No fim,
   desmarque a caixinha de abrir o programa** e clique em "Concluir". (Assim o programa abre pelo atalho, que é o que
   se quer ver. Se a caixinha ficar marcada, nada de errado acontece: o programa abre como se fosse pelo atalho.)
2. Clique duplo no atalho **"Editor de Impressão"** da Área de Trabalho. A pergunta do Windows aparece logo, antes do
   brasão e da janela (a 2ª). Ela mostra "EditorImpressao.exe" e "Editor: Desconhecido". Clique **"Não"**.
3. O programa abre normalmente. Feche-o (o X).
4. Clique duplo no atalho de novo. A pergunta aparece de novo (a 3ª). Clique **"Sim"**.
5. O programa abre. Feche-o e abra de novo: **nenhuma pergunta**.

**Tem que aparecer:** a pergunta do Windows antes de qualquer janela do programa, nas duas primeiras aberturas; a
janela do programa abre nas duas (com "Não" também); na terceira abertura, nada do Windows.

**Conferido por fora:**
- depois do "Não": "licença da pasta do programa: Usuários: ler e executar (herdada)" e "a pasta aceita gravação desta
  conta agora: False"; nada no registro diz "procurei";
- depois do "Sim": "Usuários: modificar (própria)" na pasta do programa e "(herdada)" em `current\EditorImpressao.exe`;
  "aceita gravação: True"; "motor do Kraken no lugar (conferido): True"; `packages\: (vazia)` e `ultima-boa\: (não
  existe)` (a primeira versão do instalador não baixa nada e não tem "última boa"); no registro, "procurei: nenhuma
  versão nova (esta é a 1.9.0)";
- "Programas e Recursos: Editor de Impressão 1.9.0".
- O Editor antigo de 01/09 e o ajudante antigo **já não estão no seu PC** (conferido em 25/11: nem a pasta, nem a
  entrada em Programas e Recursos, nem a tarefa do Windows): nada a tirar; o registro não diz que tirou nada.

**Print:** foto do celular das três perguntas (`p01a-instalador`, `p01b-pergunta-nao`, `p01c-pergunta-sim`); print do
programa aberto depois do "Não" (`p01d-abriu-com-nao`).

(D-733, D-735, D-741, D-805, D-806, D-834, D-837, D-857, D-788)

---

## Passo 2 — Uma versão nova, "Reiniciar agora" (5 min)

**Para que serve:** a atualização mais comum: abre, aparece o aviso, "Reiniciar agora", a janelinha do Velopack, e o
programa volta já na versão nova. Ela é testada uma vez, ganha a marca de aprovada, e o pacote dela é guardado como
"última boa", copiado do próprio computador, sem internet.

**A gerente faz:**
1. `PY P\fonte_da_prova.py liberar 1.9.1` (tem de terminar com "conferido: tudo certo").
2. Quando o aviso aparecer e ANTES do seu clique: `PY P\fonte_da_prova.py sem-resposta` (a "internet" cai: assim se vê
   que a guarda da última boa não precisa dela).
3. Depois que o programa voltar: `PY P\fonte_da_prova.py com-resposta` e `PY P\conferir_instalacao.py`.

**Você clica:** abre o programa pelo atalho; espera o aviso (alguns segundos); clica **"Reiniciar agora"**.

**Tem que aparecer:**
- o aviso, título **"Versão nova do programa"**, com: "Chegou uma versão nova do Editor de Impressão." / "Salve o seu
  trabalho e reinicie o programa para usar a versão nova." / "Se escolher "Depois", você pode atualizar quando fechar o
  programa." e os botões **"Reiniciar agora"** e **"Depois"**;
- a janela fecha; aparece a janelinha do Velopack (algo como "Atualizando para a versão 1.9.1..."); ela some; alguns
  segundos sem nada (o teste rápido da versão nova); a janela do programa abre.

**Conferido por fora:** "versão em current\sq.version: 1.9.1"; `ultima-boa\` com o pacote 1.9.1, a assinatura e a marca
`.aprovada`; no registro, "a versão 1.9.1 passou no teste rápido e está guardada como a última boa". "Programas e
Recursos" continua dizendo 1.9.0 (é esperado: o Velopack não consegue mudar esse número sem licença; visto no
experimento de 23/11). Feche e abra de novo: na vigia, **nenhum** processo com `--teste-rapido` (a aprovada não é
testada de novo).

**Print:** o aviso (`p02a-aviso`), a janelinha do Velopack (`p02b-janelinha`).

(D-715, D-720, D-875, D-832, D-856, D-869, D-851, D-854)

---

## Passo 3 — Outra versão, pelo "Depois" (8 min)

**Para que serve:** o caminho do "Depois": a pergunta ao fechar; com "Não", nada troca e o aviso volta na próxima
abertura; com "Sim", a troca acontece com o programa fechado e a próxima abertura já vem na versão nova, sem espera.

**A gerente faz:** `PY P\fonte_da_prova.py liberar 1.9.2`. Depois de cada fechar, `PY P\conferir_instalacao.py`.

**Você clica:**
1. Abre pelo atalho; aviso; **"Depois"**. Feche o programa (o X).
2. Aparece **"Atualizar agora?"**. Clique **"Não"**. O programa fecha.
3. Abre de novo: o aviso volta. **"Depois"**. Feche.
4. "Atualizar agora?": **"Sim"**. O programa fecha; aparece a janelinha do Velopack; ela some e **nada mais abre** (é
   assim: depois do "Sim" o programa não aparece sozinho).
5. Quando a gerente disser (a vigia mostra o fim da conferência por trás), abra pelo atalho: a janela abre direto.

**Tem que aparecer:** a pergunta com o título **"Atualizar agora?"**, o texto **"Quer atualizar o programa agora, ao
fechar?"** e os botões **"Sim"** e **"Não"**; depois do "Não", o aviso de novo; depois do "Sim", só a janelinha do
Velopack.

**Conferido por fora:** depois do "Não": "current\sq.version: 1.9.1" e o pacote 1.9.2 em `packages\` (baixado,
esperando). Depois do "Sim": "1.9.2"; na vigia, o processo com `--conferir-a-versao-nova 1.9.1 1.9.2 --sem-janela`
começou e terminou sem janela; `ultima-boa\` com a 1.9.2.

**Print:** "Atualizar agora?" (`p03a-ao-fechar`), o aviso de novo depois do "Não" (`p03b-aviso-volta`).

(D-769, D-794, D-831, D-835)

---

## Passo 4 — Uma versão que não funciona, e a volta à mão (15 min)

**Para que serve:** ver o que o Kaique vê quando uma versão nova sai com defeito: a caixa do próprio Windows avisando,
o programa tentando abrir assim mesmo, e a versão com defeito não sendo testada de novo. E provar como você volta à
mão para a versão boa, e que a correção publicada por cima é oferecida.

**A versão com defeito (1.9.3):** foi montada **sem um arquivo do programa** (`ui\tela_final.py`), de propósito: a
janela principal não consegue abrir. É o mesmo tipo de defeito do instalador que saiu sem os modelos em 25/09: o
pacote passa por todas as conferências do publicar (elas olham os modelos, as peças e o Visual C++, não o código), e
só o teste rápido no computador pega. Não estraga nada: os projetos não são tocados.

**A gerente faz:** `PY P\fonte_da_prova.py liberar 1.9.3`.

**Você clica:**
1. Abre pelo atalho; aviso; **"Reiniciar agora"**. A janelinha do Velopack; alguns segundos sem nada.
2. Aparece uma caixa do Windows, título **"Atualização"**: **"A versão nova não funcionou. Não desinstale nada. Avise o
   Samuel."** e o botão OK. Clique **OK**.
3. O programa tenta abrir: aparece a caixa **"Um momento — Aconteceu um problema inesperado, mas o programa continua
   funcionando."** (é a que fica para depois). Clique no botão dela. O programa fecha.
4. Abre pelo atalho de novo: **só a caixa "Um momento"** (a do Windows não aparece de novo, e a versão não é testada
   de novo). Clique e o programa fecha.

**A volta à mão (você só olha; nenhuma pergunta do Windows):**
1. `PY P\conferir_instalacao.py 20 --somar` → "a última boa: 1.9.2" e "o pacote da última boa confere com a assinatura
   do Samuel: SIM".
2. Copiar o pacote guardado para fora da pasta do programa (o Velopack apaga o pacote que ele não consegue abrir; a
   cópia protege o guardado):
   `New-Item -ItemType Directory -Force "C:\EditorImpressaoProva\prova-a-vista-25-11\volta-a-mao" | Out-Null; Copy-Item "C:\Program Files\EditorImpressaoPrograma\ultima-boa\EditorImpressaoPrograma-1.9.2-full.nupkg" "C:\EditorImpressaoProva\prova-a-vista-25-11\volta-a-mao\"`
3. Pedir ao próprio Velopack que troque para ela, sem reabrir:
   `Start-Process -Wait "C:\Program Files\EditorImpressaoPrograma\Update.exe" -ArgumentList 'apply','--norestart','--package','"C:\EditorImpressaoProva\prova-a-vista-25-11\volta-a-mao\EditorImpressaoPrograma-1.9.2-full.nupkg"'`
   (a janelinha do Velopack aparece e some).
4. `PY P\conferir_instalacao.py` → "current\sq.version: 1.9.2".
5. **Você:** abre pelo atalho: a 1.9.2 abre normalmente, sem teste e sem aviso (a 1.9.3 não é oferecida de novo).
6. A correção: `PY P\fonte_da_prova.py liberar 1.9.4`. **Você:** fecha, abre; o aviso; **"Reiniciar agora"**; a
   janelinha; abre na 1.9.4.

Por que `--norestart` e o atalho depois: se o Velopack reabrisse o programa sozinho, o programa podia ver o Velopack
ainda saindo e fechar sem mostrar nada (a regra que protege o clique no atalho durante uma troca). Com o atalho depois,
não há essa dúvida.

**Tem que aparecer:** a caixa do Windows, palavra por palavra; depois dela, a tentativa de abrir; na abertura seguinte,
nenhuma caixa do Windows.

**Conferido por fora:** depois do OK: "current\sq.version: 1.9.3"; bilhete "reprovadas ['1.9.3']"; frases vistas com
`reprovada-1.9.3`; `ultima-boa\` ainda com a 1.9.2; no registro, "teste rápido da versão instalada: erro ao abrir:
ModuleNotFoundError: No module named 'ui.tela_final'" e nada pedido ao Velopack. Na abertura seguinte, nenhum
`--teste-rapido` na vigia. Depois da volta à mão: 1.9.2; depois da correção: 1.9.4 e `ultima-boa\` com a 1.9.4.

**Print:** a caixa do Windows (`p04a-caixa-do-windows`), a caixa "Um momento" (`p04b-um-momento`), a janelinha da volta
à mão (`p04c-volta-a-mao`), a 1.9.2 aberta (`p04d-de-volta`), o aviso da 1.9.4 (`p04e-correcao`).

(D-867, D-868, D-869, D-871, D-857, D-881)

---

## Passo 5 — Uma versão com a assinatura falsa (3 min)

**Para que serve:** uma versão publicada sem a sua assinatura (como se alguém de fora tivesse posto uma versão no
lugar) não é instalada, e o Kaique é avisado uma vez.

**A versão (1.9.5):** montada normal; depois, a assinatura dela foi trocada por uma feita com outra chave (a sua
verdadeira está guardada fora da pasta das versões).

**A gerente faz:** `PY P\fonte_da_prova.py liberar 1.9.5`; depois, `PY P\conferir_instalacao.py`.

**Você clica:** abre pelo atalho; espera uns segundos; aparece uma caixa; **OK**. Fecha e abre de novo: nada.

**Tem que aparecer:** título **"Atualização"**, **"Chegou uma versão nova, mas ela não foi instalada porque não tem a
assinatura do Samuel. O programa continua funcionando. Avise o Samuel."**; nenhum aviso de versão nova; na abertura
seguinte, nada.

**Conferido por fora:** a 1.9.5 **não** está em `packages\` (nem foi baixada); frases vistas com `recusada-1.9.5`; no
registro, "assinatura recusada".

**Print:** a caixa (`p05-assinatura-falsa`).

(D-724, D-778 frase 2, D-848)

---

## Passo 7 — O motor de achar texto fora do lugar (4 min)

(Antes do 6, porque usa a versão 1.9.6 antes de ela ser baixada.)

**Para que serve:** sem o motor no lugar, nenhuma versão nova é anunciada nem trocada.

**A gerente faz:** com o programa **fechado**: `PY P\por_de_lado.py motor-de-lado`; `PY P\fonte_da_prova.py liberar
1.9.6`. Depois da sua abertura: espera 1 minuto e `PY P\conferir_instalacao.py`. No fim: programa fechado e `PY
P\por_de_lado.py motor-de-volta`.

**Você clica:** abre pelo atalho; trabalha um minuto; **nenhum aviso**; fecha (nenhuma pergunta ao fechar).

**Conferido por fora:** no registro, "o motor do Kraken não está no lugar (...): nenhuma versão é procurada nem
anunciada"; a 1.9.6 não está em `packages\`. (Funciona assim só depois de uma troca: na versão do instalador, o motor
seria posto de novo do arquivo que vem junto.)

**Print:** o programa aberto sem aviso (`p07-sem-motor`).

(D-833, D-790)

---

## Passo 6 — A "internet" que para de responder (6 min) — no lugar do passo 6 do plano

**Para que serve:** com a versão nova já baixada, mesmo sem resposta da internet, o aviso volta (o programa usa o que
já chegou). Sem nada baixado, sem resposta: nada na tela, nada quebrado.

**A gerente faz:** (motor de volta) nada antes da 1ª abertura. Depois do 1º fechar: `PY P\fonte_da_prova.py
sem-resposta`. No fim: `PY P\fonte_da_prova.py com-resposta`.

**Você clica:**
1. Abre pelo atalho; o aviso da 1.9.6 (agora baixada); **"Depois"**; fecha; "Atualizar agora?": **"Não"**.
2. Abre de novo (a "internet" parou): **o aviso aparece mesmo assim**; **"Depois"**; fecha; **"Não"**.

**Conferido por fora:** no registro, "não consegui procurar a versão nova (...); a 1.9.6 já está baixada" e "a versão
1.9.6 tem a assinatura do Samuel e o pacote dela já está no computador: nada a baixar".

**Print:** o aviso sem resposta da "internet" (`p06-aviso-sem-internet`).

(D-859; o passo do plano: D-773, ver "Perguntas para você")

---

## Passo 9 — O atualizador posto de lado (5 min)

**Para que serve:** quando um antivírus põe de lado o atualizador do programa (`Update.exe`), "Reiniciar agora" diz o
que houve, a janela não fecha; quando ele volta, o aviso volta.

**A gerente faz:** com o aviso na tela e ANTES do seu clique: `PY P\por_de_lado.py atualizador-de-lado`. Depois do seu
fechar: `PY P\por_de_lado.py atualizador-de-volta`.

**Você clica:** abre; o aviso; (a gerente põe de lado); **"Reiniciar agora"**; a caixa; **OK**; a janela continua
aberta; fecha (o X): **nenhuma pergunta**. (A gerente põe de volta.) Abre de novo: o aviso volta.

**Tem que aparecer:** título **"Atualização"**, **"Não deu para atualizar: o atualizador do programa sumiu do
computador. O programa continua funcionando. Avise o Samuel."**

**Print:** a caixa (`p09a-sem-atualizador`), o aviso de volta (`p09b-aviso-volta`).

(D-870, D-873)

---

## Passo 10 — O Windows recusando a troca, duas vezes (8 min)

**Para que serve:** quando o Windows não deixa trocar (um arquivo preso por outro programa), o programa volta na versão
de antes e avisa; e avisa de novo na segunda vez.

**Como se "prende":** um processo da gerente entra na pasta `current` do programa e fica nela; o Windows não deixa
trocar o nome de uma pasta em uso (o mesmo erro da prova de 22/11). Ninguém é fechado à força: o processo sai sozinho
quando a gerente manda soltar.

**A gerente faz:** com o aviso na tela: por trás, `PY P\por_de_lado.py segurar-a-pasta 900`; confere com `PY
P\por_de_lado.py estado` ("SEGURADA"). Depois das duas recusas: `PY P\por_de_lado.py soltar`.

**Você clica:**
1. **"Reiniciar agora"**. A janela fecha; a janelinha do Velopack (cerca de 1 minuto: ele tenta 10 vezes); ela some.
2. Aparece a caixa do Windows, título **"Atualização"**: **"A atualização não deu certo. O programa continua na versão
   de antes e funcionando. Avise o Samuel."** → **OK**. A janela abre na 1.9.4, e o aviso aparece de novo.
3. **"Reiniciar agora"** outra vez: a mesma coisa, **a mesma caixa de novo**. **OK**.

**Conferido por fora:** "current\sq.version: 1.9.4" depois de cada recusa; frases vistas com dois nomes `troca-1.9.6-...`
(um por recusa).

**Print:** a caixa da 1ª recusa (`p10a-recusa-1`), a da 2ª (`p10b-recusa-2`).

(D-839, D-877)

---

## Passo 8 — Um clique no atalho durante a troca (3 min)

**Para que serve:** se o Kaique clicar no atalho enquanto a janelinha do Velopack está na tela, a troca termina do
mesmo jeito.

**A gerente faz:** (a pasta já solta, passo 10) nada; depois, `PY P\conferir_instalacao.py`.

**Você clica:** **"Reiniciar agora"**; com a janelinha do Velopack na tela, **clique duplo no atalho**; nada abre; a
janelinha some; a janela abre na versão nova.

**Conferido por fora:** "current\sq.version: 1.9.6"; na vigia, o processo do seu clique começou e terminou sem janela;
`ultima-boa\` com a 1.9.6.

**Print:** a janelinha com o clique (`p08-clique-durante`).

(D-770 na parte do clique; D-832)

---

## Passo 11 — Desinstalar (5 min; 1 pergunta do Windows)

**Para que serve:** o desinstalar tira a pasta inteira do programa (com o motor, os pacotes e a última boa) e deixa os
seus projetos.

**A gerente faz:** com o programa fechado, abre "Configurações > Aplicativos > Aplicativos instalados", acha "Editor de
Impressão" e clica "Desinstalar". Depois: `PY P\conferir_instalacao.py`, `PY P\projetos_antes_e_depois.py tirar
depois` e `PY P\projetos_antes_e_depois.py comparar antes depois`.

**Você clica:** "Sim" na pergunta do Windows.

**Conferido por fora:** "não está instalado" (a pasta `C:\Program Files\EditorImpressaoPrograma` sumiu inteira);
"nenhuma entrada Editor de Impressão"; os atalhos sumiram; a comparação diz **"DENTRO DE projetos\: NADA MUDOU, nada
sumiu"** (fora de `projetos\`, mudam só o que o programa sempre grava: as configurações e as frases vistas).

**Print:** foto da pergunta (`p11a-pergunta`), a lista de aplicativos sem o Editor (`p11b-desinstalado`).

(D-788, D-729, D-882)

---

## Passo 12 — As medidas (lidas da vigia, sem mais nada na tela)

**A gerente faz:** `PY P\vigiar_janelas.py` já parou? Se não: cria `C:\EditorImpressaoProva\prova-a-vista-25-11\registros\parar-a-vigia`. Lê o registro
`C:\EditorImpressaoProva\prova-a-vista-25-11\registros\vigia-<data>-<hora>.txt`.

- **Quanto a abertura leva:** de "PROCESSO COMEÇOU ... EditorImpressao.exe" (o do clique) até "JANELA APARECEU" da
  janela principal. Medir em três aberturas: (a) sem versão nova (passo 2, depois da troca: o atualizador só olha);
  (b) com a versão nova sendo procurada e baixada por trás (passo 2, a primeira); (c) a abertura logo depois do "Sim"
  (passo 1, item 5, com o motor ainda sendo posto no lugar por trás). Se (a), (b) e (c) derem parecido, o atualizador não
  atrasa a janela.
- **Os segundos sem nada na tela depois da troca:** de "JANELA SUMIU" da janelinha do Velopack até "JANELA APARECEU"
  da janela do programa (passos 2, 4 e 8). É o teste rápido.

---

## O que fica no seu PC depois da prova, e como limpar

| O que | Onde | Tamanho | Como limpar |
|---|---|---|---|
| as versões de prova (estoque, publicadas, a fonte, a volta à mão, os registros, os prints) | `C:\EditorImpressaoProva\prova-a-vista-25-11\` | uns 5 GB (a fonte não ocupa: são os mesmos arquivos) | apagar a pasta, com o seu "sim" (sem pergunta do Windows) |
| a cópia de trabalho que montou as versões | `D:\programas\EditorImpressao\.claude\worktrees\prova-a-vista-montagem\` | uns 3 GB (com a cópia dos modelos, sem junção) | `git worktree remove --force` pela gerente (não há junção dentro) |
| o arquivo da fonte de teste e o registro da atualização | `C:\ProgramData\EditorImpressao\` | pequeno | apagar a pasta, **com licença** (1 pergunta do Windows), com o seu "sim" |
| o registro do próprio Velopack | `%LOCALAPPDATA%\velopack\` | pequeno | apagar, com o seu "sim" |
| as frases já vistas e a pasta da reabertura, dentro da sua pasta de dados | `%LOCALAPPDATA%\EditorImpressao\atualizacao-avisos-vistos.json` e `troca\` | pequeno | **não se mexe** sem você pedir (é a pasta dos projetos; D-882) |
| o rascunho do publicar | `%LOCALAPPDATA%\EditorImpressao-publicar\rascunho\` | o publicar apaga o dele (conferido em cada versão) | nada |
| sobras de provas antigas (não são desta prova) | `C:\EditorImpressaoProva\versoes`, `versoes 2`, `versoes 3`, `servida` e os `.log`; `%LOCALAPPDATA%\EditorImpressao\troca\` (de 23/11) | uns 3,5 GB | já estavam antes; só com o seu "sim" |

---

## Perguntas para você

### 1. O passo da "internet caindo no meio do download"

**Do que se trata.** No plano de 18/11 você escolheu que, nas provas, as versões viessem de uma janelinha visível no
seu PC, que faz o papel da internet: "fechar a janela prova a internet caindo no meio" (a opção A daquele dia).

**O que acontece hoje.** O programa novo só sabe ler as versões de prova de uma **pasta** do computador, não dessa
janelinha. De uma pasta, o download é uma cópia de 2 a 5 segundos: não dá para "cortar a internet" no meio. Isso não é
defeito que o Kaique veria (no notebook dele as versões vêm do GitHub pela internet de verdade): é a ferramenta de
prova que não encaixa no programa novo. Foi achado agora, na preparação.

**O que acontece no caso de verdade** (lido no código do Velopack, não provado): se a internet cair no meio, o pedaço
baixado fica guardado com outro nome, nada aparece na tela, e a próxima abertura baixa de novo.

**O que você escolhe:**
- **A (sugestão): fazer a prova sem esse passo.** No lugar dele, o passo 6 deste roteiro ("a internet para de
  responder", com e sem a versão já baixada). A queda no meio do download fica para ser provada junto com os testes à
  distância, que já estão na fila de depois da entrega. Nada do que já funciona muda.
- **B: mudar o programa** para ele também saber ler a janelinha nas provas. É código novo no programa: precisa da
  rodada de testes, de quem tenta quebrar (curto) e de montar as versões de novo (cerca de 1 hora de máquina). A prova
  fica para depois disso.
- Só comentário também vale.

**Situação:** achado na preparação; nada mudou no programa.

---

*Preparação: os comandos marcados "rodado antes" no ONDE-PAREI da preparação foram rodados numa pasta de ensaio, sem
nada na sua tela. Os que só rodam na prova estão listados lá também.*
