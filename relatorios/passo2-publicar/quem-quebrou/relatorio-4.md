# Passo 2 do plano da parte do Windows: quarta conferência de quem tentou quebrar (20/11/2026)

Sou um agente novo nesta volta (D-815). Não escrevi este código e não fiz as voltas 1 a 3. Não mexi no código do
outro.

O que **não** fiz:
- não rodei o vpk, o PyInstaller nem o `gh release`;
- não publiquei nada e não pedi licença de administrador;
- não abri janela na tela do Samuel.

O que rodei de verdade no Windows (só o que não pede licença):
- a peça do Windows, com cópias do `hostname.exe` numa pasta minha;
- o `gh --version`, que não fala com o GitHub.

Tudo rodou em cópias do código (`git archive` de `595cc293` e de `5f96975b`), na pasta de rascunho desta conversa, um
arquivo de teste por vez.

## Pedido

- Papel: quebrador
- Commit de partida: c75566a1
- Ramo: passo2-publicar-2026-11-19

## Arquivos que vou mexer

- `publicar_versao_kaique.py`
- `empacotar.py`
- `core/windows.py`
- `tests/test_windows_peca.py`
- `tests/test_empacotar.py`
- `tests/test_publicar_*.py`
- `relatorios/passo2-publicar/`

(Copiado do pacote sem mudar. Na prática só escrevi em `relatorios/passo2-publicar/quem-quebrou/`: este relatório,
nos três formatos, e a pasta `anexos-4/`.)

## Veredito

**NÃO ESTÁ PRONTO para a prova à vista.** Falta um conserto pequeno.

**Os 12 achados do relatório 3 estão consertados pela causa.**
- Depois do pedido de liberar, o publicar não apaga mais nada (D-816). Isso não depende de leitura nenhuma.
- O nome do programa é lido uma vez só, como o Windows o completa.
- O gh e o vpk passam pelo mesmo laço da peça.

Desliguei 10 proteções numa cópia, uma por vez. Os testes acusaram 6. As 4 que passaram estão explicadas nos achados
3, 7 e 8.

**Achei um problema médio.** Há três frases do publicar que mandam rodar `--apagar <versão>` sem dizer o destino.
- Na pasta das provas, quem segue a frase apaga no GitHub, e não na pasta.
- O `--apagar` apaga a versão do GitHub mesmo liberada, com a etiqueta.
- Esta volta criou o lugar único que escreve esse comando certo (`comando_de_apagar`), mas três frases antigas
  continuam escritas à mão, sem o destino.

Os outros achados são baixos: frases que dizem mais do que aconteceu, três proteções sem teste, um vizinho do nome e um
texto que promete demais.

Pela D-775, volta para quem escreveu. Não escrevo "PRONTO PARA CONFERIR" (D-798): falta a prova à vista. Nunca
"aprovado": só o Samuel aprova.

## Decisões que esta tarefa precisa cumprir

- D-816 "A , mas onde estamos antes de você fazer qualquer processo". Aqui: **cumprida**.
  - Depois do pedido de liberar, nada é apagado, nos dois destinos (código lido e testes com 1, 2, 3 e 10 leituras
    atrasadas).
  - Antes do pedido, o rascunho continua sendo apagado na hora (mutação A1: desligar isso faz um teste falhar).
  - Fica um caso de borda: o achado 4.
- D-767 "não faça mais nada escodindo ou de mentira". Aqui: a peça do Windows rodou de verdade (o nome, o gh no laço). O
  GitHub e o vpk só com as peças de mentira dos testes, que provam só a lógica em volta.
- D-773 "A". Aqui: a frase nova diz como conferir e o comando de apagar. O achado 1 mostra uma frase antiga que manda
  apagar no destino errado.
- D-775 "ok". Aqui: tentei quebrar, sem pergunta do Windows. O resultado vai à gerente.
- D-776 "Sim, no C só tem que cuidar para não encher o disco C inteiro". Aqui: **cumprida** no download para somar
  (vai ao rascunho do C:, passa pela vigia e entra na conta; mutações do outro V11 a V15 e a minha A7).
- D-795 "ok". Aqui: nada mudou no Setup.exe (conferido no código).
- D-811 "ok". Aqui: **pela metade**. Três proteções passam com o teste desligado (achados 3 e 7).
- D-812 "ok". Aqui: a frase da D-816 não usa dado do destino. "Pedi" ou "não pedi" vem do caminho do código. Um furo: o
  achado 2.
- D-813 "ok". Aqui: o nome, rodado em 34 jeitos de escrever (anexo `e5-nomes-resultado.txt`). Passa um: o fluxo
  escondido de um arquivo (achado 5).
- D-798 "fechou". Aqui: sem o rótulo de pronto.

## O que li

- `.claude/agents/verificador.md` e o `CLAUDE.md` inteiro (§4.7, §11.8 e o §11.12 com os 6 pontos).
- `memoria/INDICE.md` e `memoria/catalogo-de-erros.md` (famílias F1 a F10).
- O meu pacote (`anexos/pacote-quem-quebra-volta4.md`). Os textos da D-811 a D-813 e da D-816 vieram do pedido da
  gerente.
- Os relatórios 1, 2 e 3 de quem tentou quebrar.
- No formulário do escritor (`ONDE-PAREI.md`), as seções da volta 4: decisões, "O que o agente que tentou quebrar
  achou", "Cada proteção", "De onde vem cada dado", "Ressalvas" e "A prova de verdade".
- Os anexos `reversao-volta4-*` e `volta4-nome-e-loja*`.
- O código da volta 4 (`git diff 5f96975b 595cc293`):
  - em `publicar_versao_kaique.py`: `_Destino`, `apagar_publicacao`, `_frase_depois_do_pedido_de_liberar`,
    `publicar_arquivos`, `DestinoGitHub._gh` e `soma`, a conta em `publicar` e `publicar_motor`, e `main`;
  - em `core/windows.py`: `_como_o_windows_completa`, `_caminho_do_programa`, `_por_que_recusa`,
    `_por_que_nao_e_programa`, `rodar_em_grupo`, `abrir_em_grupo` (com `capturar`), `ProgramaEmGrupo.esperar`,
    `gravar_no_disco` e `_gravar_por_inteiro`;
  - em `empacotar.py`: `rodar_vpk`, `copiar_inteiro`, `zipar_motor` e `vigia_do_espaco`.
- Peça de fora (D-813):
  - Microsoft Learn: "File path formats on Windows systems", na parte do corte dos pontos e espaços do fim (citada pelo
    outro e conferida rodando);
  - a ordem em que o CreateProcess procura um nome sozinho;
  - o `communicate` do Python.
  - O que o Windows aceita de verdade eu não deduzi: rodei (E5 e E6).

## O que conferi nas falhas, nas peças de fora e nos caminhos

### Os 12 achados do relatório 3, um por um

| Achado | O que vi | Desligado numa cópia, o teste acusa? |
|---|---|---|
| 1 (D-816) | Depois do pedido de liberar, nenhum caminho chama o apagar. Procurei todos os apagar do código (o caminho de erro, o Ctrl+C, a vigia, o `--apagar`, o `_fim`, a conferência do fim): o `_fim` só apaga o rascunho do C: e a conferência só lê. | sim: V1 do outro; minha A2 (marcar "pedi" só depois de o liberar responder) |
| 1, a outra metade | Antes do pedido de liberar, o erro continua apagando o rascunho. | sim: minha A1 (`test_a_leitura_de_volta_que_nao_bate_nao_libera_e_apaga_o_rascunho_do_destino`) |
| 2 | Nome lido uma vez, como o Windows completa. Rodei 34 jeitos (abaixo). | sim: minhas A3 (só o nome sozinho) e A4 (só o caminho com pasta) |
| 3 | A frase diz se pediu. Achei o vizinho ao contrário: "pedi" sem ter pedido (meu achado 2). | V4 a V7 do outro, sim; minha A5 (o gh de verdade sem a resposta), **não** (meu achado 3) |
| 4 | O criar foi para dentro do `try`. "Não achei" logo depois de criar não vira "sumiu". | sim: V2 e V3 |
| 5 | Escrito como limite da peça. | não se aplica |
| 6 | Frase própria para o programa que não deixa ler. | sim: V9 |
| 7 | O download para somar vai ao rascunho, pela vigia, e entra na conta; a subpasta é apagada. | sim: V11 a V15; minha A7 (a subpasta não apagada); minha A10 (o destino não volta ao estado de antes no fim), **não** (observação, achado 8) |
| 8 | `windows.rodar_em_grupo` é o único laço do gh e do vpk. Procurei outros `subprocess`: só sobram o PyInstaller e o Inno Setup, que não são deste achado. O gh de verdade (`gh --version`) rodou pelo laço, com a saída guardada (anexo E6). | V16 a V19b, sim; minha A9 (o grupo sem guardar a saída), sim; minha A6 (sem juntar a saída depois de fechar), **não** (observação, achado 8) |
| 9 | O texto cru está lá; o arquivo compila sem aviso. | não se aplica |
| 10 | Teste novo; a V10 do outro prova que ele cobra. | sim |
| 11 | O `os.fsync` está na cópia, no motor comprimido e na peça. O texto promete mais do que o código faz (meu achado 6). | sim: V20 a V23 |
| 12 | Os dois arquivos do desinstalar continuam falhando no PC (25 e 5), como no relatório 3. Família F4; está em "Ideias e bugs". | não se aplica |

**Reversão.** Rodei os testes novos no código de `5f96975b` (anexo `reversao-testes-novos-no-codigo-antigo.txt`).
- Em `test_publicar_versao.py`, os 22 testes novos falham.
- Em `test_windows_peca.py`, falham 4 de 5. O que passa é o do achado 10: a proteção já existia.
- Bate com o anexo do outro: 26 de 27.

**O teste antigo que saiu** (`test_volta3_achado5_o_liberar_que_falha_e_continua_rascunho_apaga_o_rascunho`).
- **A troca está certa.** Ela muda só o que a D-816 mudou.
- O mesmo caso (o mesmo destino de prova, `_DestinoQueNaoLibera`, na pasta) é cobrado em
  `test_d816_o_liberar_que_falha_e_fica_rascunho_nao_apaga_e_diz_o_comando[pasta]`, e também no GitHub.
- O teste novo prova que o jeito antigo saiu: o rascunho continua e a frase diz o comando. E prova que o comando
  apaga.
- A outra metade da decisão antiga (o erro antes de liberar apaga) continua cobrada (mutação A1).
- Essa troca vai ao Samuel pela gerente (§11.8).

### O nome do programa, rodado de verdade (E5, anexo `e5-nomes-resultado.txt`)

Usei cópias do `hostname.exe` chamadas `pwsh.exe` e `Update.exe`, numa pasta minha posta só no PATH do meu processo,
mais o `whoami.exe` da pasta do Windows.
- A peça recusa 30 dos 34 jeitos de escrever. Exemplos: o ponto e o espaço no fim, maiúsculas, sem extensão, o nome
  curto (8.3), `\\?\`, `\\.\`, `\??\`, o caminho relativo, a barra no fim, `pasta\..\`, o nome sozinho pelo PATH, as
  aspas, o TAB, o `whoami.exe.` sozinho e com a pasta, o `System32\..\System32` e o caminho sem a letra do disco.
- Os 4 que a peça deixa passar: três o Windows também não roda (as aspas no meio, o `::$DATA` e o `\??\UNC\localhost`).
  O quarto ele roda: **o fluxo escondido `nada.txt:pwsh.exe`** (meu achado 5).
- A peça não recusa nada que o Windows deixaria rodar por um desses nomes, fora esse.

### O laço único e o Ctrl+C

- O vpk e o gh chamam `rodar_em_grupo` com a mesma vigia, o mesmo tempo e o mesmo fechar.
- No Ctrl+C, os dois fecham o grupo e repassam a interrupção (`except BaseException: fechar_tudo; raise`).
- A diferença entre os dois está só no que se faz com o resultado:
  - o vpk escreve no terminal e devolve a frase;
  - o gh guarda a saída e levanta Parou ou SemResposta.
- O caso igual dos dois é cobrado pelo teste do achado 8 (as mutações V16 a V19b do outro).

### O que mudou na peça do passo 1 (§11.8)

O `_gravar_por_inteiro` agora pede `fsync`. Ele grava os scripts, a tarefa, o aviso, o segredo e a ficha da pasta
segura.

Rodei os arquivos ao redor, um por vez, no código novo (anexo `arredor-um-arquivo-por-vez.txt`):

| Arquivo de teste | Resultado |
|---|---|
| `test_windows_peca.py` | 67 passaram, 2 pulados |
| `test_publicar_versao.py` | 70 passaram |
| `test_publicar_servidor.py` | 14 passaram |
| `test_publicar_motor.py` | 12 passaram |
| `test_empacotar.py` | 41 passaram |
| `test_windows_janela_de_prova.py` | 10 passaram |
| `test_decisoes_atualizacao.py` | 38 passaram |
| `test_decisoes_ajudante_da_atualizacao.py` | 37 passaram |
| `test_decisoes_testes_a_distancia.py` | 13 passaram |
| `test_decisoes_brasao.py` | 22 passaram |
| `test_decisoes_desinstalar.py` e `_pasta.py` | 25 e 5 falham, como antes (achado 12 do relatório 3, F4) |

- As frases da recusa só são usadas em `core/windows.py` e nos testes dele.
- O nome novo da função antiga só é chamado ali.
- Não vi nada já escolhido que mudou.
- Fica o que o outro já escreveu: o lado com licença de administrador não rodou.

### A rodada do GitHub 44748591841

- Consultei duas vezes, com 5 minutos de intervalo.
- O resultado: success na 3ª tentativa.
- O registro diz "TESTADO_SHA: 324cebb3" em todas as partes, inclusive na parte 2 da 3ª tentativa (código trocado às
  14:48).
- Entre `595cc293` e `324cebb3` só mudou o `ONDE-PAREI.md` (`git diff --stat`). Então o código testado é o desta volta.

## Caminhos que o outro não listou

1. **A frase que manda rodar o `--apagar` quando a publicação já existe** (o começo de `publicar_arquivos`, o de
   `publicar` e o de `publicar_motor`). Ela não passa pelo `comando_de_apagar` (achado 1).
2. **A leitura que fica sem resposta dentro do apagar do rascunho no GitHub**, antes de pedir (achado 2).
3. **O gh que nem abre no pedido de liberar** (achado 4).
4. **O programa num fluxo escondido de outro arquivo** (`arquivo:nome.exe`; achado 5).
5. **As outras gravações "nome provisório e depois troca"** que o texto de `gravar_no_disco` diz que passam por ela
   (achado 6).

## Falhas não pensadas e resultado não conferido

- **Peça duplicada (§11.12.1):** o comando de apagar escrito à mão em três frases, ao lado do lugar único novo
  (achado 1).
- **Dá como feito o que não fez (F5):**
  - "pedi para apagar" sem ter pedido (achado 2);
  - "pedi para liberar" com o gh sem abrir (achado 4).
- **Proteção sem teste (F3):**
  - a troca "o gh fechado por tempo vira sem resposta" no `_gh` de verdade (achado 3);
  - a frase "outra pessoa liberou no meio" pelo caminho do GitHub (achado 3).
- **O vizinho passa (F2):** o fluxo escondido (achado 5).
- **O escrito não bate com o código (F7):** "todo código que grava num nome provisório" (achado 6).
- **F1 e F9:** não achei caso novo. Nenhuma junção, nada mudou no Windows, o repositório não ficou raso.

## As regras que conferi

- **§11.12 (uma regra, um lugar):**
  - cumprida na recusa da peça, no laço e na frase da D-816;
  - não cumprida no comando de apagar (achado 1).
- **§11.12.2 (nada dado como feito sem conferir):** os achados 2 e 4.
- **§11.12.3 (a lista das falhas):** faltam os caminhos 1 a 5 acima.
- **§11.12.4 e D-767:** a peça rodou de verdade. O GitHub e o vpk ficam para a prova à vista.
- **§11.12.6 e D-813:** o nome foi rodado de verdade; o fluxo escondido passa (achado 5).
- **§11.8:** os testes antigos passam. A única troca de teste é a da D-816, e está certa.
- **§4.7 e D-811:** a reversão bate (26 de 27). Das minhas 10 mutações, 6 foram acusadas.
- **D-816:** cumprida (acima).
- **D-776:** cumprida no download para somar.
- **D-798:** sem rótulo de pronto.
- **D-809:** não criei junção.
- **CLAUDE.md §10.9:** só criei e apaguei dentro da minha pasta de rascunho.

## Achados

1. **MÉDIO: na pasta das provas, três frases mandam apagar no GitHub.**
   - Onde: `publicar_versao_kaique.py`, nas linhas 685 (`publicar_arquivos`, "sobrou um rascunho"), 898 (`publicar`,
     "já existe") e 1025 (`publicar_motor`, "já existe").
   - As três escrevem `--apagar {etiqueta}` à mão, sem o `--pasta` do destino.
   - Sem `--pasta`, o `--apagar` vai ao GitHub. Lá ele apaga a publicação em qualquer situação: liberada também, com a
     etiqueta (`--cleanup-tag`).
   - Provado com o gh de mentira dos testes (Q4, anexos `test_quebra4.py.txt` e `testes_q4-resultado.txt`):
     - na pasta sobra um rascunho da v9.9.9;
     - o publicar para com "apague o rascunho com --apagar v9.9.9";
     - rodei exatamente esse comando;
     - a v9.9.9 **liberada** do GitHub foi apagada, com a etiqueta;
     - o rascunho da pasta continua lá.
   - Já era assim antes desta volta. Mas a volta 4 criou `comando_de_apagar` como o lugar único desse comando (o
     `--pasta` incluído) e deixou estas três cópias sem ele: é a conta duplicada do §11.12.
   - Quando pode acontecer: quando a mesma versão existe na pasta das provas e no GitHub.
   - O que pedir: as três frases passam a usar `destino.comando_de_apagar(etiqueta)`, com um teste que segue a frase de
     cada uma na pasta e confere que o GitHub não é tocado.

2. **BAIXO: "pedi para apagar" sem ter pedido.**
   - Onde: `publicar_versao_kaique.py:562` (`DestinoGitHub.apagar_rascunho` lê a situação antes de pedir) e `:624`
     (`apagar_publicacao`, `except SemResposta`).
   - O que acontece:
     - o envio falha, antes de liberar;
     - a leitura de antes de apagar responde;
     - a segunda leitura, dentro do `apagar_rascunho`, fica sem resposta (o gh é fechado por tempo);
     - a frase diz "pedi para apagar v9.9.9 ... e não deu para conferir se sumiu";
     - **nenhum pedido de apagar saiu**, e o rascunho continua no GitHub (Q1).
   - É o vizinho ao contrário do achado 3 do relatório 3.
   - O efeito é pequeno: a frase manda conferir e dá o comando.
   - O que pedir: a leitura de dentro do apagar, quando falha, não vira "pedi". Por exemplo, ler fora do pedido, ou o
     destino dizer à frase se o `delete` chegou a sair. Com um teste.

3. **BAIXO: duas proteções do apagar sem teste.**
   - **(a)** `publicar_versao_kaique.py:453`: no `_gh` de verdade, o gh fechado por tempo ou pela vigia vira
     `SemResposta`.
     - Troquei por `Parou` comum (mutação A5): os 70 testes passam.
     - Os testes do achado 3 levantam `SemResposta` direto do gh de mentira, e não passam por essa linha.
     - Sem ela, um pedido de apagar que saiu e ficou sem resposta volta a dizer "não apaguei" (o achado 3 do relatório
       3 de volta).
   - **(b)** `publicar_versao_kaique.py:622-623` (`except PublicacaoLiberada: raise` dentro de `apagar_publicacao`).
     - Tirei (mutação A8): os 70 passam.
     - A frase "outra pessoa ou outro publicar a liberou no meio" pelo caminho do GitHub não é cobrada. Nada é apagado a
       mais; muda só a frase.
   - O que pedir: um teste para cada uma (D-811). Para o (a), um gh de prova que demora e o `limite_s` curto, como o
     do achado 8.

4. **BAIXO: "pedi para liberar" quando o gh nem abriu.**
   - Onde: `publicar_versao_kaique.py:701` (a marca vem antes de `destino.liberar`) e `:449` (o `_gh` que não abre
     levanta `Parou` comum).
   - O que acontece:
     - o gh não abre no pedido de liberar, e nada saiu do PC;
     - mesmo assim, o publicar diz "pedi para liberar" e deixa o rascunho no GitHub (Q2).
   - Pela D-816, antes do pedido o rascunho seria apagado. Quando o gh responde com erro, não dá para saber, e ficar
     sem apagar está certo. Mas aqui o código sabe que nada saiu (`abriu: False`).
   - Não apaga nada a mais. Deixa um rascunho e uma frase que não é verdade.
   - O que pedir: a gerente decide. Pode ficar como está, mas escrito como escolha; ou o "não abriu" não conta como
     pedido.

5. **BAIXO: o programa num fluxo escondido de outro arquivo passa pela lista de nomes.**
   - Onde: `core/windows.py:1191` (`_por_que_recusa`, `nome = caminho.name.lower()`).
   - O que acontece:
     - gravei uma cópia do `hostname.exe` como fluxo escondido `nada.txt:pwsh.exe`;
     - o Windows roda esse caminho;
     - a peça lê o nome como `nada.txt:pwsh.exe`, não acha "pwsh" na lista e deixa rodar (E5).
   - É da mesma família do limite do achado 5 do relatório 3: é preciso gravar uma cópia de propósito.
   - O que pedir:
     - escrever como limite, junto do achado 5;
     - ou comparar também o nome depois do último ":" (o nome do fluxo).

6. **BAIXO: o texto de `gravar_no_disco` promete mais do que o código faz.**
   - Onde: `core/windows.py:1015`.
   - O texto diz "todo código que grava num nome provisório e depois troca pelo nome certo chama esta função".
   - Não é verdade. A ficha do motor, que é deste passo, grava assim sem ela (`montar_motor_kraken.py:586-588`). Também
     o PDF de saída (`core/pipeline.py`) e os projetos (`projetos.py`), que não são deste passo.
   - Família F7.
   - O que pedir: corrigir o texto, nomeando quem chama. Ou a ficha do motor passa a usar a função. Os outros dois não
     devem mudar sem pedido (§11.8).

7. **OBSERVAÇÃO: o `--apagar` apaga também uma versão liberada.**
   - Rodei o comando da frase da D-816 numa versão liberada na pasta, e ela foi apagada (Q3).
   - O outro já escreveu isso nas Ressalvas ("não foi pedido; fica escrito"). Confere.
   - Com o achado 1, o risco aumenta: o comando pode ir ao destino errado.

8. **OBSERVAÇÃO: duas mutações sem efeito que se veja hoje.**
   - A6: o laço não junta a saída depois de fechar. Hoje ninguém usa essa saída.
   - A10: o destino não volta ao estado de antes no fim do publicar. Hoje ninguém reaproveita o destino.
   - Não pedem conserto. No máximo, uma linha em "Cada proteção" dizendo que são arrumação.

9. **OBSERVAÇÃO (não é deste passo): os dois arquivos do desinstalar continuam falhando no PC.**
   - São 25 e 5 testes, como no relatório 3: família F4.
   - Já está em "Ideias e bugs" para a Lista de bugs.

## O que falta para a prova à vista

1. Quem escreveu consertar o achado 1, com o teste que falha sem o conserto. De preferência também os achados 2, 3 e 6.
   Os achados 4 e 5 a gerente decide.
2. Uma rodada do GitHub sobre o conserto, e outro agente novo para conferir (D-815).
3. Na prova à vista, além do roteiro do outro (itens 10 a 12):
   - no fim, rodar o `--apagar` **com** `--pasta` na pasta e **sem** ele no GitHub, e conferir em cada destino que o
     outro não foi tocado;
   - olhar no Gerenciador de Tarefas que o gh de verdade some depois de cada pedido.

## Para a gerente: o que ficou fora do projeto

Tudo fica na pasta de rascunho desta conversa, em
`C:\Users\fotog\AppData\Local\Temp\claude\b9ca076ad002e817\85bc5c33-3dbe-4d9d-9032-bb0a97954262\scratchpad\v4\`:
- as cópias do código: `novo\` (`595cc293`, com o meu `tests\test_quebra4.py`), `velho\` (`5f96975b`, com os dois
  arquivos de teste novos por cima) e `mut\` (as mutações; cada arquivo foi devolvido ao original);
- os casos do E5 (`casos5\`): as cópias do `hostname.exe` e o fluxo escondido;
- os scripts e o registro da rodada.

Não apaguei nada fora dela. Os processos de prova terminaram sozinhos.

Nada mudou no Windows: nenhuma tarefa, licença, pergunta de administrador ou janela. O PATH mudou só dentro do meu
processo de Python. Nenhuma junção foi criada.

O repositório não ficou raso: `--is-shallow-repository` deu false antes e depois.

No projeto, só escrevi este relatório (`.md`, `.html`, `.pdf`) e a pasta `quem-quebrou/anexos-4/`, num commit só
com esses arquivos (`[skip ci]`), como o relatório 3. O pacote da volta 4 (`anexos/pacote-quem-quebra-volta4.md`), que
não é meu, ficou de fora do commit.
