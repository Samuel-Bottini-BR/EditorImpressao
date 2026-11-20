# Passo 2 do plano da parte do Windows: quinta conferência de quem tentou quebrar (20/11/2026)

Sou um agente novo nesta volta (D-815). Não escrevi este código e não fiz as voltas 1 a 4. Não mexi no código do
outro.

O que **não** fiz:

- não rodei o vpk, o PyInstaller nem o `gh release`;
- não publiquei nada e não pedi licença de administrador;
- não abri janela na tela do Samuel.

O que rodei de verdade no Windows (só o que não pede licença):

- a peça do Windows, com cópias do `hostname.exe` gravadas como fluxo escondido numa pasta minha;
- o gh, o vpk e o Python com `--version` (não falam com o GitHub);
- o gh e o Python abertos parados e fechados sem nunca soltar (para contar as linhas deles).

Tudo rodou em cópias do código (`git archive` de `35ec0c27` e de `595cc293`), na pasta de rascunho desta conversa, um
arquivo de teste por vez.

## Pedido

- Papel: quebrador
- Commit de partida: 384df3f6
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
nos três formatos, e a pasta `anexos-5/`. O pacote `anexos/pacote-quem-quebra-volta5.md`, que a gerente gerou, vai no
mesmo commit, como ela pediu.)

## Veredito

**Nenhum achado médio ou grave.** Achei três problemas baixos e algumas observações.

**Os 6 achados do relatório 4 estão consertados pela causa.**

- As três frases que mandavam apagar no GitHub estando na pasta agora usam o lugar único do comando (`comando_de_apagar`).
  Todas as frases com `--apagar` saem dele.
- "Pedi para apagar" só sai quando o pedido de apagar saiu de verdade.
- O gh que nem abriu no pedido de liberar não conta como pedido. Procurei de propósito um gh que abriu e fosse contado
  como "nem abriu". No uso normal não existe (detalhe abaixo).
- O programa escrito como fluxo escondido é recusado. Rodei 21 jeitos de escrever: o código antigo deixava passar 15
  que o Windows roda; o novo, nenhum. E nenhum caminho que o programa usa passou a ser recusado.

Desliguei 8 proteções numa cópia, uma por vez, diferentes das 10 do outro. Os testes acusaram 7. A que passou é o
achado 1 abaixo.

Os três baixos:

1. uma proteção sem teste: o pedido de apagar em que o gh nem abre;
2. a frase do motor que falta, na pasta das provas, manda rodar `--motor` sem o `--pasta` (o vizinho do achado 1 do
   relatório 4);
3. o caminho de rede é recusado com a frase errada ("tem função própria"); já era assim antes desta volta.

Pela D-775, a gerente decide se volta para quem escreveu ou se segue para a prova à vista. Não escrevo "PRONTO PARA
CONFERIR" (D-798): falta a prova à vista. Nunca "aprovado": só o Samuel aprova.

## Decisões que esta tarefa precisa cumprir

- D-816 "A , mas onde estamos antes de você fazer qualquer processo". Aqui: **cumprida**.
  - Depois do pedido de liberar, nada é apagado. A minha mutação X1 (qualquer erro do liberar contar como "não pedi")
    faz 13 testes falharem, entre eles todos os `test_d816_*`.
  - O único caso que agora apaga é o gh que nem começou. Isso cabe na decisão ("Antes do pedido de liberar, erro no
    meio continua apagando o rascunho na hora"): nada saiu do PC. Os limites dessa conta estão na observação 4.
- D-817 "pode". Aqui: **cumprida**. O teste antigo saiu (só um comentário ficou no lugar, linha 1003) e o
  `test_d816_o_liberar_que_falha_e_fica_rascunho_nao_apaga_e_diz_o_comando` está lá e passa. Nesta volta nenhum teste
  antigo mudou: o diff dos testes de `595cc293` a `35ec0c27` só acrescenta.
- D-767 "não faça mais nada escodindo ou de mentira". Aqui: a peça rodou de verdade (os fluxos, os caminhos legítimos,
  o gh parado). O GitHub e o vpk só com as peças de mentira dos testes, que provam só a lógica em volta.
- D-773 "A". Aqui: as frases de "já existe" e "sobrou um rascunho" dão o comando do destino certo. Uma frase vizinha
  ainda dá um comando sem o destino (achado 2).
- D-775 "ok". Aqui: tentei quebrar, sem pergunta do Windows. O resultado vai à gerente.
- D-776 "Sim, no C só tem que cuidar para não encher o disco C inteiro". Aqui: nada desta volta toca a conta do espaço
  nem a vigia (conferido no diff). Os testes do empacotar e do publicar passam.
- D-795 "ok". Aqui: nada mudou no Setup.exe (conferido no diff).
- D-811 "ok". Aqui: **pela metade**. A reversão do outro bate (8 de 9; refiz no código de `595cc293`). Das minhas 8
  mutações, 7 acusadas; uma passa sem teste (achado 1).
- D-812 "ok". Aqui: "nada saiu" vem do que a peça fez ao abrir o gh (`abriu: False`), e "pedi para apagar" vem de qual
  pedido ficou sem resposta. Nenhum dos dois vem de uma leitura do GitHub. Conferido no código.
- D-813 "ok". Aqui: o que o Windows faz com o ":" eu não deduzi: rodei 21 jeitos de escrever (anexo E7) e os caminhos
  legítimos (anexo E8). A recusa compara o caminho completado pelo Windows, que é a coisa de verdade.
- D-798 "fechou". Aqui: sem o rótulo de pronto.

## O que li

- `.claude/agents/verificador.md` e o `CLAUDE.md` inteiro (§4.7, §11.8 e o §11.12 com os 6 pontos).
- `memoria/INDICE.md` e `memoria/catalogo-de-erros.md` (famílias F1 a F10).
- O meu pacote (`anexos/pacote-quem-quebra-volta5.md`). Os textos da D-811 a D-813, D-816 e D-817 vieram do pedido da
  gerente: o Livro deste ramo é mais velho.
- Os relatórios 1 a 4 de quem tentou quebrar (o 4 inteiro; dos outros, os achados e o que pediam).
- No formulário do escritor (`ONDE-PAREI.md`), as seções da volta 5: "Onde parei", decisões, "O que já está escolhido e
  testado", "Como fica para quem usa", "A causa, a regra e todos os caminhos", "O que pode falhar", "O que li da peça
  de fora", "Testes", "Caminho e função", "Cada proteção", "De onde vem cada dado", "Ressalvas", "O que o agente que
  tentou quebrar achou" e "A prova de verdade".
- Os anexos `reversao-volta5-*`.
- O código: `git diff 595cc293 35ec0c27` inteiro e, para contexto, o de `5f96975b` a `595cc293`. Li inteiras, no código
  novo: `DestinoGitHub` (`_gh`, `liberar`, `apagar`, `apagar_rascunho`, `_pedir_para_apagar`), `apagar_publicacao`,
  `_frase_depois_do_pedido_de_liberar`, `publicar_arquivos`, `obter_motor_publicado`, `main`; em `core/windows.py`,
  `_como_o_windows_completa`, `_caminho_do_programa`, `_por_que_nao_e_programa`, `_e_fluxo_escondido`,
  `_por_que_recusa`, `abrir_em_grupo`, `_soltar_o_programa_parado`, `ProgramaEmGrupo` e `rodar_em_grupo`.
- Peça de fora (D-813): as duas páginas da Microsoft que o outro cita ("File Streams" e "Naming Files, Paths, and
  Namespaces") e a do CREATE_SUSPENDED. O que elas dizem eu conferi rodando (E7 e E9), sem confiar só no texto.

## O que conferi nas falhas, nas peças de fora e nos caminhos

### Os 6 achados do relatório 4, um por um

| Achado | O que vi | Desligado numa cópia, o teste acusa? |
|---|---|---|
| 1 (frases sem o `--pasta`) | As três usam `destino.comando_de_apagar`. Procurei `--apagar` no projeto: fora o cabeçalho e o `main`, toda frase sai do lugar único. | sim: W1a a W1c do outro; minha X6 (a pasta sem o `--pasta`): 3 falham |
| 2 ("pedi" sem ter pedido) | `ApagarSemResposta` só nasce em `_pedir_para_apagar`, em volta do `delete`, e só é lida em `apagar_publicacao`. A leitura sem resposta antes do pedido vira "não apaguei". | sim: W2 e W2b do outro |
| 3a (gh fechado por tempo) | O teste novo usa um gh de prova de verdade e o laço de verdade. | sim: W3a do outro; minha X2 (o laço dizer "não abriu" no tempo esgotado): 3 falham; minha X7 (ignorar o tempo novo): 1 falha |
| 3b (liberada antes do pedido) | Teste novo no GitHub de mentira. | sim: W3b do outro |
| 4 (gh que nem abriu) | Ver "O gh que nem abriu" abaixo. | sim: W4 e W4b do outro; minha X1 (qualquer erro do liberar): 13 falham. **Mas** a minha X3 passa (achado 1) |
| 5 (fluxo escondido) | Ver "O fluxo escondido" abaixo. | sim: W5 do outro; minhas X4, X5 e X8: 1 falha em cada |
| 6 (texto de `gravar_no_disco`) | O texto agora nomeia quem passa e quem não passa. Bate com o código. | não se aplica (só texto) |

**Reversão** (anexo `reversao-testes-novos-no-codigo-antigo.txt`). Rodei os testes novos no código de `595cc293`:

- em `test_windows_peca.py`, o teste do fluxo falha (o fluxo passava);
- em `test_publicar_versao.py`, 7 de 8 falham; o do achado 3b passa (a proteção já existia), como o outro escreveu.
- Bate com o anexo dele: 8 de 9.
- Um detalhe: os dois testes do achado 4 falham no código antigo porque o nome `NadaSaiu` não existia, e não pelo
  defeito em si. A prova de que eles cobram o comportamento é a mutação W4 do outro e a minha X1.

### O gh que nem abriu (achado 4): procurei um gh que abriu e fosse contado como "nem abriu"

O `NadaSaiu` nasce num lugar só: `DestinoGitHub._gh`, quando o laço da peça devolve `abriu: False`. O laço só devolve
isso quando `abrir_em_grupo` devolve "nada". Conferi cada caso do pedido da gerente:

- **Tempo esgotado logo no começo:** o tempo só é olhado depois de o programa abrir e ser solto, dentro do laço. Sai
  como "abriu, parou por tempo" (`SemResposta`), nunca como "nem abriu". A minha X2 prova que um teste acusa se isso
  mudar.
- **O grupo que fecha antes de soltar:** os três casos (não pôs no grupo, não confirmou, não soltou) acontecem com o
  gh ainda parado. Pela Microsoft (CREATE_SUSPENDED: "does not run until the ResumeThread function is called"), ele não
  rodou nada. Um caso de borda: ver a observação 4.
- **Erro de leitura da saída:** a leitura acontece depois de abrir. Um erro ali sobe como exceção comum, não como
  `NadaSaiu`. No liberar, isso conta como pedido: nada é apagado (o lado seguro).
- **O antivírus:** se ele impede o gh de abrir, o Windows recusa a criação, e nada rodou: `NadaSaiu` está certo. Se
  ele fecha o gh depois de abrir, o laço vê "saiu com o código X": conta como pedido, nada é apagado.
- **O Ctrl+C:** sobe como interrupção, nunca como `NadaSaiu`. No liberar, nada é apagado.
- O `DestinoGitHub.liberar` faz um pedido só ao gh (o `edit`). Então "o liberar levantou NadaSaiu" quer dizer "o
  `edit` não saiu". Isso não está escrito no texto do `liberar` (observação 5).

### O fluxo escondido (achado 5), rodado de verdade (E7, anexos `e7-*`)

Gravei uma cópia do `hostname.exe` como fluxo em três lugares: num `.txt`, num `.exe` de verdade (que começa com "MZ")
e numa pasta. Depois rodei 21 jeitos de escrever, cada um sem a peça (o Windows roda?) e pela peça (ela recusa?).

| Jeito de escrever | O Windows roda? | Código antigo | Código novo |
|---|---|---|---|
| `nada.txt:pwsh.exe`, `inocente.exe:pwsh.exe`, `inocente.exe:outro.exe` | sim | passa | recusa (fluxo) |
| com `\\?\` e com `\\.\` na frente | sim | passa | recusa (fluxo) |
| com `\??\` na frente | não | recusa | recusa |
| relativo `.\inocente.exe:pwsh.exe` e `C:inocente.exe:pwsh.exe` (sem barra) | sim | passa | recusa (fluxo) |
| relativo sem pasta `inocente.exe:pwsh.exe` | não | passa | recusa (fluxo) |
| maiúsculas, barras `/`, ponto no fim | sim | passa | recusa (fluxo) |
| nome curto (8.3), com e sem `\\?\` | sim | passa | recusa (fluxo) |
| fluxo de uma pasta (`pastinha:pwsh.exe`) | **sim** | passa | recusa (fluxo) |
| `...:pwsh.exe:$DATA` | não | passa | recusa (fluxo) |
| caminho de rede (`\\localhost\C$\...` e `\\?\UNC\...`) | sim | recusa | recusa (frase errada, achado 3) |

- **Resultado: o código antigo deixava passar 15 jeitos que o Windows roda; o novo, nenhum.**
- O fluxo de uma pasta o Windows também roda. A regra nova pega, mas o teste do outro não tem esse caso (observação 6).
- No relatório, troquei o que o `hostname.exe` escreveu (o nome do computador) por "rodou".

### Os caminhos legítimos não passaram a ser recusados (E8, anexo `e8-*`)

Rodei a recusa no código velho e no novo, e o programa de verdade com `--version`:

- o gh (pelo PATH, pelo lugar fixo, com `\\?\`, com `\\.\`, com nome curto e com barras `/`);
- o vpk (pelo `achar_vpk` e com `\\?\`);
- o Python do projeto (direto, com `\\?\` e com `\\.\`);
- os nomes sozinhos (`python`, `gh`, `vpk`) e o `D:python.exe`.

**Os resultados são iguais nos dois códigos: tudo passa.** O `Update.exe` e o `pwsh.exe` continuam recusados de
propósito (lista de função própria), também iguais. Esses dois eu não rodei.

### O tempo novo e a exceção nova: um lugar só? (§11.12)

- `LIMITE_DO_PEDIDO_S` é o tempo de fábrica de todo pedido ao gh, lido num lugar só (`_gh`). O envio e o download
  continuam com o próprio `3 * 3600`, escrito duas vezes. Já era assim antes desta volta; não é desvio para um caso.
- `ApagarSemResposta` nasce num lugar e é lida num lugar. A pasta das provas nunca a levanta, e está certo: lá não há
  "sem resposta".
- O `except NadaSaiu` em `publicar_arquivos` fica no único lugar onde se decide "pedi ou não pedi para liberar". Não é
  desvio: vale igual para a versão e para o motor, que passam pelo mesmo `publicar_arquivos`.

### O que já funcionava em volta (§11.8; anexo `arredor-um-arquivo-por-vez.txt`)

| Arquivo de teste (código `35ec0c27`, um por vez) | Resultado |
|---|---|
| `test_windows_peca.py` | 68 passaram, 2 pulados |
| `test_publicar_versao.py` | 78 passaram |
| `test_publicar_servidor.py` | 14 passaram |
| `test_publicar_motor.py` | 12 passaram |
| `test_empacotar.py` | 41 passaram |
| `test_windows_janela_de_prova.py` | 10 passaram |
| `test_decisoes_atualizacao.py` | 38 passaram |
| `test_decisoes_ajudante_da_atualizacao.py` | 37 passaram |
| `test_decisoes_testes_a_distancia.py` | 13 passaram |
| `test_decisoes_brasao.py` | 22 passaram |
| `test_nome_do_pacote.py` | 5 passaram |

Bate com o que o outro escreveu. Não rodei os dois arquivos do desinstalar, que já falhavam no PC antes (observação 9
do relatório 4).

### A rodada do GitHub 44766224353 (anexo `rodada-44766224353-o-que-foi-testado.txt`)

- Consultei uma vez.
- O resultado: success, na 2ª tentativa.
- O registro diz "TESTADO_SHA: 2bb04bf2" em todas as 52 linhas.
- De `35ec0c27` a `2bb04bf2` só mudaram o `ONDE-PAREI.md` e os três anexos da reversão. Então o código testado é o desta
  volta.
- A falha da 1ª tentativa (`test_decisoes_gravura_a_mao.py`) é de um arquivo que nada deste passo toca. Não o rodei de
  novo: a gerente já o rodou no PC (15 passaram).

## Caminhos que o outro não listou

1. **O pedido de apagar em que o gh nem abre** (`NadaSaiu` dentro de `_pedir_para_apagar`). Funciona, mas nenhum teste
   o percorre (achado 1).
2. **A frase do motor que falta** (`obter_motor_publicado`, "publique o motor antes (--motor)"). É uma frase com
   comando que não passa pelo destino (achado 2).
3. **O fluxo de uma pasta** (`pasta:programa.exe`). A regra pega, o teste não tem (observação 6).
4. **O programa aberto parado com mais de uma linha** (observação 4).

## Falhas não pensadas e resultado não conferido

- **Proteção sem teste (F3):** o "nem abriu" do pedido de apagar (achado 1).
- **O vizinho passa (F2):** o comando do motor sem o destino (achado 2).
- **O escrito não bate com o código (F7):** a frase do caminho de rede (achado 3); o `liberar` não diz que faz um
  pedido só (observação 5).
- **Dá como feito o que não fez (F5):** não achei caso novo. "Nada saiu" só é dito quando o gh não rodou (fora o caso de
  borda da observação 4).
- **F1 e F9:** não achei caso novo. Nenhuma junção, nada mudou no Windows, o repositório não ficou raso.

## As regras que conferi

- **§11.12 (uma regra, um lugar):** cumprida no comando de apagar, na exceção nova, no tempo novo e na recusa do fluxo.
  Fica de fora a frase do motor (achado 2).
- **§11.12.2 (nada dado como feito sem conferir):** "nada saiu" vem do que a peça fez; "foi apagada" continua vindo da
  leitura de volta.
- **§11.12.3 (a lista das falhas):** a do outro cobre a volta 5; faltam os caminhos 1 a 4 acima.
- **§11.12.4 e D-767:** a peça rodou de verdade. O GitHub e o vpk ficam para a prova à vista.
- **§11.12.6 e D-813:** a leitura do outro sobre o ":" confere com o que rodei.
- **§11.8:** os testes ao redor passam; nesta volta nenhum teste antigo mudou.
- **§4.7 e D-811:** a reversão bate (8 de 9). Das minhas 8 mutações, 7 foram acusadas.
- **D-816 e D-817:** cumpridas (acima).
- **D-798:** sem rótulo de pronto.
- **D-809:** não criei junção.
- **CLAUDE.md §10.9:** só criei arquivos dentro da minha pasta de rascunho e da pasta deste relatório. Não apaguei nada.

## Achados

1. **BAIXO: o pedido de apagar em que o gh nem abre não tem teste.**
   - Onde: `publicar_versao_kaique.py:112` (`class NadaSaiu(Parou)`) e `:592-596` (`_pedir_para_apagar` só troca
     `SemResposta` por "pedi").
   - O que protege: se o gh nem abre no pedido de apagar, a frase diz "não apaguei". Isso está certo hoje porque
     `NadaSaiu` não é um caso de `SemResposta`.
   - Desliguei (mutação X3: `NadaSaiu` passa a ser um caso de `SemResposta`). Os 78 testes passam.
   - Com essa troca, a frase diria "pedi para apagar ... e não deu para conferir se sumiu", sem nada ter saído do PC.
   - Provei com um teste meu (`anexos-5/test_quebra5.py.txt`, Q5a, e `q5-resultado.txt`): passa no código novo e falha
     com a X3.
   - O que pedir: um teste do projeto para esse caso (D-811). O meu Q5a serve de modelo.

2. **BAIXO: na pasta das provas, a frase do motor que falta dá o comando sem o destino.**
   - Onde: `publicar_versao_kaique.py:766-767` (`obter_motor_publicado`): "não está publicado em a pasta ...: publique
     o motor antes (--motor)".
   - Na pasta das provas, quem roda `--motor` ao pé da letra publica no GitHub: cria o rascunho, envia, lê de volta e
     **libera** o motor lá. A D-773 só deixa um rascunho no GitHub durante a prova, apagado no fim.
   - Provado com o ambiente dos testes (Q5b): a frase sai exatamente assim, sem o `--pasta`.
   - É o vizinho do achado 1 do relatório 4 (F2). Não apaga nada, por isso é baixo. Mas deixa uma publicação liberada no
     GitHub, que pega o número do motor.
   - A frase já diz o destino ("em a pasta ..."), e o roteiro da prova publica o motor na pasta antes (passo 3). Isso
     diminui a chance.
   - O que pedir: o destino escrever também este comando (por exemplo, um `comando_de_publicar_o_motor` ao lado do
     `comando_de_apagar`, com o `--pasta`), com um teste como o do achado 1.

3. **BAIXO (já era assim antes desta volta): o caminho de rede é recusado com a frase errada.**
   - Onde: `core/windows.py:1207-1209` (`_por_que_recusa`): quando `_caminho_do_programa` devolve "nada" (caminho de
     rede, ou que o Windows não completa), a frase é "este programa do Windows tem função própria na peça: use a função
     dela".
   - Para `\\localhost\C$\...\programa.exe` a frase manda usar uma função que não existe. É o mesmo tipo do achado 6 do
     relatório 3 (F7), que deu frase própria ao "não consegui ler".
   - Rodado (E7): a recusa está certa; só a frase está errada.
   - O que pedir: uma frase própria para o caminho de rede ou que o Windows não completa. Pode ficar para depois: não
     muda nada do que roda.

4. **OBSERVAÇÃO: o "nada saiu" supõe que o programa aberto parado tem uma linha só.**
   - Onde: `core/windows.py`, `_soltar_o_programa_parado`. Ele solta as linhas uma por uma. Se a primeira fosse solta e
     a segunda falhasse, o programa teria rodado um instante, e o laço diria `abriu: False` (`NadaSaiu`). No liberar,
     isso faria o publicar apagar o rascunho.
   - Medido (E9): o gh e o Python, abertos parados 30 vezes cada, tinham sempre uma linha só. A Microsoft diz que a
     linha principal só roda depois de solta.
   - Só um outro programa que ponha uma linha dentro do gh parado (um antivírus que faça isso) criaria o caso. Mesmo
     então, o gh seria fechado em microssegundos, antes de conseguir falar com a rede.
   - Não pede conserto. No máximo, uma linha nas Ressalvas.

5. **OBSERVAÇÃO: o `liberar` do GitHub não diz que faz um pedido só.**
   - A regra do achado 4 ("o liberar levantou NadaSaiu, então não pedi") só vale porque `DestinoGitHub.liberar` faz um
     pedido só ao gh. Se alguém acrescentar ali uma leitura depois do `edit`, um `NadaSaiu` dessa leitura faria o
     publicar apagar depois do pedido de liberar, contra a D-816.
   - O que pedir: uma linha no texto do `liberar` dizendo isso (e, se a gerente quiser, um teste que confira que o
     `liberar` faz um pedido só).

6. **OBSERVAÇÃO: o fluxo de uma pasta não está no teste.**
   - O Windows roda `pastinha:pwsh.exe` (E7). A regra nova recusa, mas o teste do outro só grava fluxo num `.txt`.
   - Pode entrar no mesmo teste, como mais um jeito.

## O que falta para a prova à vista

1. A gerente decide se os achados 1 a 3 voltam para quem escreveu antes da prova. Nenhum muda o que acontece no GitHub
   ou na pasta quando tudo dá certo.
2. Na prova à vista, além do roteiro do outro (itens 1 a 12) e do que o relatório 4 acrescentou:
   - se der sem risco, provocar o gh que não abre no pedido de liberar (por exemplo, o gh recusado pela peça), e
     conferir na tela que o rascunho é apagado e que a frase diz "foi apagada (conferido)";
   - na pasta das provas, ver que toda frase que manda rodar um comando traz o `--pasta`.

## Para a gerente: o que ficou fora do projeto

Tudo fica na pasta de rascunho desta conversa, em
`C:\Users\fotog\AppData\Local\Temp\claude\b9ca076ad002e817\85bc5c33-3dbe-4d9d-9032-bb0a97954262\scratchpad\v5\`:

- as cópias do código: `novo\` (`35ec0c27`, com o meu `tests\test_quebra5.py`), `velho\` (`595cc293`, com os dois
  arquivos de teste novos por cima) e `mut\` (as mutações; cada arquivo foi devolvido ao original, conferido);
- os casos do E7 (`casos7\` e `casos7v\`): as cópias do `hostname.exe` e os fluxos escondidos;
- os scripts e os resultados.

Não apaguei nada fora dela. A pasta `v4\` ao lado é do agente da volta 4; não mexi nela. Os processos de prova
terminaram sozinhos ou foram fechados por mim (os abertos parados, no E9).

Nada mudou no Windows: nenhuma tarefa, licença, pergunta de administrador ou janela. Nenhuma junção foi criada.

O repositório não ficou raso: `--is-shallow-repository` deu false antes e depois.

No projeto, só escrevi este relatório (`.md`, `.html`, `.pdf`) e a pasta `quem-quebrou/anexos-5/`, mais o pacote da
volta 5 (`anexos/pacote-quem-quebra-volta5.md`), num commit só (`[skip ci]`).
