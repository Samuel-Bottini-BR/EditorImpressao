# Passo 0 do plano da parte do Windows: segunda conferência de quem tentou quebrar (19/11/2026)

Esta é a segunda volta do mesmo verificador, que não escreveu o passo 0. Conferi os consertos dos 19 achados do
primeiro relatório (`relatorio.md`, nesta pasta) e tentei quebrar de novo: pelo mesmo caminho e por um caminho vizinho.
Não mexi no código entregue. As provas rodaram na cópia temporária, fora do projeto.

## Pedido

- Papel: quebrador
- Commit de partida: 7c39c9d5
- Ramo: passo0-porteiro-2026-11-19

## Arquivos que vou mexer

- `relatorios/passo0-2026-11-19/quem-quebrou/`

## Veredito

**NÃO ESTÁ PRONTO**, mas está bem mais perto.

- Dos 19 achados:
  - 14 estão consertados de verdade;
  - 3 ficaram pela metade (6, 7 e 8);
  - 2 não foram consertados, e o porquê se sustenta (11 e 17).
- **Um problema novo reabre os achados 6 e 7.** O "sim" do Samuel que a lista exige é conferido no Livro só por um
  pedaço de texto. Um agente põe o próprio erro na lista com o "sim" `{"decisao": "D-791", "palavras": "sim"}`, ou até
  com `"palavras": "a"`, e passa no gancho e na proteção do GitHub. Isso fura a regra "nada entra nela sem o 'sim'
  dele" (D-791).
- **O texto para o Samuel ainda não tem print que prove.** A imagem continua sendo o próprio texto. E a pergunta dos 22
  lugares pergunta de novo, em parte, o que ele já decidiu em 19/11 (D-800).

## O que li

- O `relatorios/passo0-2026-11-19/ONDE-PAREI.md` novo, com as seções "Como ficou cada achado", "Perguntas para a
  gerente", "Testes", "Ressalvas" e "Perguntas para o Samuel".
- O código mudado de `ee520a12` a `7c39c9d5`, com o último código em `76fed2ee`: `porteiro.py`,
  `leitura_do_codigo.py`, `porteiro_mudancas.py`, `protecao.py` (novo), `excecoes.py`, `formulario.py`, `__main__.py`,
  `conversa_com_o_git.py`, `tabela_arquivos.py` e `texto_para_o_samuel.py`.
- Os testes `tests/test_conferencias_*.py`, entre eles `tests/test_conferencias_protecao.py` (novo), e
  `tests/conferencias_excecoes.json`, que agora tem 125 lugares em 118 itens.
- O texto `lista-de-excecoes-para-o-samuel.md` e a imagem `.png` dele, e os anexos `pacote-passo1.md` e
  `pacote-passo0.md`.
- As rodadas do GitHub:
  - 44461501923 ("success");
  - 44461329846 ("success"). Li o registro desta: o ramo de prova com a lista "valendo" rodou
    `test_conferencias_excecoes.py` com 12 testes passando e nenhum parado. Então o teste que barra o repositório rodou
    de verdade.

## O que conferi nas falhas, nas peças de fora e nos caminhos

**Recontagem.** Contei de novo com um script meu, que tira os comentários e as docstrings do seu próprio jeito e usa as
expressões novas.

- Achei 107 lugares de conversa com o Windows, 2 de `DETACHED_PROCESS` e 2 de licença de pasta. Com os 14 números de
  decisão, dá 125. **Bate.**
- Por passo também bate: 1, 29, 50 e 17, que somam 97 no plano; mais 6 "depois da entrega" e 22 "fora do plano".
- Procurei alarme falso nos 107. Não achei palavra que só esteja em comentário, em docstring ou em nome de arquivo.
  - `[powershell]::Create()` (`atualizacao.py:883`) é o PowerShell rodando um pedaço por dentro do próprio script.
    Conta como caso de borda, não como erro.
  - Os falsos alarmes possíveis no futuro são pequenos: `creationflags=0`, "self-service", "hku:" (achado N5).

**Cada um dos 19, pelo mesmo caminho e pelo vizinho:**

1. **Consertado.** Na cópia, com a lista "valendo" e um "sim" no formato novo, os 12 testes de
   `tests/test_conferencias_excecoes.py` passam. Na rodada de prova do GitHub, o teste que barra o repositório rodou e
   passou.
2. **Consertado em grande parte.** As 23 linhas novas da busca acham os 14 disfarces do primeiro relatório, menos os
   textos em pedaços, que estão nas ressalvas. Pelo vizinho, ainda passam (achados N2 e N3):
   - `["sc", "create", ...]` em lista: o `sc` só é achado com espaço depois;
   - `net stop` e `net start`;
   - `taskkill` e `Stop-Process`;
   - `New-Object -ComObject WScript.Shell`: o COM só é achado quando é o das tarefas;
   - `ctypes.CDLL` e `ctypes.cdll`;
   - `Get-PhysicalDisk`, que é exatamente a leitura do tipo de disco do teste de velocidade;
   - `creationflags=f`, com o número guardado numa variável;
   - toda chamada feita por um apelido de biblioteca já pega.
3. **Consertado.** Sem `--pacote`, o formulário volta (código 1). Com o pacote de "layout", o agente que escreve
   "implementador" no ONDE-PAREI é devolvido.
4. **Consertado.** O agente de tela que mexe em `atualizacao.py` e em `tests/test_atalhos.py` é barrado: "mexeu fora de
   ui/ sem o pedido nomear o arquivo".
5. **Consertado, com a ressalva que ele mesmo escreveu.** O rótulo de quem construiu é barrado no ONDE-PAREI, numa pasta
   `quem-quebrou/` mexida junto com outro arquivo, e em `docs/quem-quebrou/`. Passam, só com aviso (achado N4):
   - a imitação, num commit que mexe só na pasta, que já é ressalva dele;
   - o rótulo numa pasta `quem-quebrou/` de **outro** trabalho;
   - o rótulo em `relatorios/quem-quebrou/` direto.
6. **Pela metade.**
   - Contra a ponta deste ramo, a proteção acusa: palavra tirada da busca (o `schtasks`), mudança da situação, mudança
     do "sim" e mudança do passo de um item.
   - Não acusa o afrouxamento pelo uso: a lista de palavras continua igual, mas a linha que junta as palavras deixa uma
     de fora. Esse caso só é pego pelo teste que tiver exemplo daquela palavra (o do `msiexec` existe e falhou). Oito
     grupos de palavras não têm exemplo nos testes (achado N3).
   - Os itens novos com "sim" forjado passam (achado N1).
   - Enquanto a versão de teste não tiver o porteiro, a proteção do GitHub fica parada. Isso está escrito.
7. **Pela metade.** O gancho barra o item novo sem "sim": provado com `antes-do-commit`, código 1. Com o "sim"
   forjado, passa, código 0 (achado N1).
8. **Pela metade.**
   - Melhorou: o caso real está escrito, há "o que ela não faz", o que acontece se ele disser "não", e "de onde veio".
     A conta bate com a lista.
   - Continua: a imagem é o próprio texto, sem print do caso real (CLAUDE.md §11.13, regra 3).
   - Novo: "Os 5 lugares [...] continuam lá" e logo depois "a conta dá 6" confunde.
   - Novo: a pergunta dos 22 inclui o teste de velocidade lendo a placa de vídeo pelo PowerShell, que ele já mandou
     para depois (achado N6).
9. **Consertado.** "D-731" num texto de `core/analise.py` agora é acusado.
10. **Consertado no caso provado.** Pelo vizinho: num texto com `{}` que não é folha de estilo (um f-string
    `f"Arquivo {nome} salvo /* conforme D-731 */"`), o número some da busca (achado N7).
11. **Não consertado; o porquê se sustenta.** É o combinado do plano (arquivo, conferência, texto e quantas), está nas
    ressalvas, e o pacote passa a mostrar os lugares da lista nos arquivos do pedido.
12. **Consertado pela metade.** O texto do pedido só dá a etiqueta de Windows quando o título tem "Windows",
    "instalador" ou "atualiza". Os títulos "Passo 5: desinstalar limpo", "Passo 2: publicar e o motor do Kraken" e "a
    pasta segura do programa" não ganham as regras de Windows num arquivo novo de `core/` (achado N8).
13. **Consertado.** A lista do Windows, as pastas de fora do projeto e quem pode escrever o rótulo de pronto agora estão
    num lugar só cada uma.
14. **Consertado.**
15. **Consertado.** A ressalva das aspas está escrita.
16. **Consertado.** O `regras_dos_agentes/` tem 17 arquivos, e o gancho cita o que a documentação do git diz.
17. **Pergunta à gerente; se sustenta.**
18. **Consertado.** A D-722 e a D-724 estão no pacote do passo 1. A barra de rolagem foi como pergunta à gerente.
19. **Consertado.** Agora usa `git ls-remote`.

## Caminhos que o outro não listou

- **Chamadas por apelido de biblioteca do Windows.** A escolha "no ctypes conta só a linha onde a biblioteca é pega" é
  razoável para não multiplicar a lista. Mas esconde coisa: uma chamada nova feita pelo mesmo apelido não é barrada, e
  o apelido pode sair da função.
  - Em `teste_velocidade.py:1746`, `return kernel32, kernel32.GetStdHandle(...)` devolve a biblioteca para quem chama.
  - Em `atualizacao.py:438`, a leitura do dono do arquivo é feita por `advapi32.GetNamedSecurityInfoW`, que não entra
    na conta. Só a linha 435, onde a biblioteca é pega, entra.
  - Isso não está escrito como ressalva (achado N2).
- **Afrouxar o porteiro pela linha que junta as palavras** (`regras_dos_agentes/porteiro.py:199`), sem tirar palavra
  nenhuma (achado N3).
- **A pasta `quem-quebrou/` de outro trabalho**, ou direto em `relatorios/` (achado N4).

## Falhas não pensadas e resultado não conferido

- **Resultado não conferido: o "sim" do Samuel.** A conferência no Livro olha só se as palavras aparecem em algum
  lugar da linha da decisão (`regras_dos_agentes/livro.py:51`). Uma letra basta (achado N1).
- **Falha não pensada.** A rodada de prova do GitHub só abriu a lista com um "sim" de mentira porque essa conferência
  aceita qualquer pedaço. Isso mostra que a conferência não separa o "sim" de verdade do inventado.
- **O pacote usado para conferir o formulário deste passo** (`anexos/pacote-passo0.md`) foi feito por quem construiu,
  no próprio ramo. É o caso de partida, mas a gerente confere se ele é mesmo o pedido dela (achado N9).

## As regras que conferi

- **CLAUDE.md §11.12:**
  - (1) uma peça só: cumprida, com as listas agora num lugar só;
  - (2) nada dado como feito sem conferir: pela metade (achado N1);
  - (3) a lista do que pode falhar: melhorou;
  - (4) peça de mentira: cumprida;
  - (6) ler a peça de fora: as fontes de `PALAVRAS_DO_WINDOWS` estão citadas.
- **CLAUDE.md §11.13**, no texto para o Samuel:
  - regras 1, 2, 5, 6, 7, 9 e 10: cumpridas, menos a parte da D-800 (achado N6);
  - regras 3 e 4: pela metade, porque não há print.
- **Cada decisão tocada:**
  - D-791: pela metade (achado N1);
  - D-792: cumprida;
  - D-796: cumprida;
  - D-798: cumprida, com a ressalva da imitação;
  - D-800: pela metade (achado N6);
  - D-784: cumprida, com o achado N8;
  - D-605 e D-637: cumpridas, porque nada mudou fora de `regras_dos_agentes/`, `ganchos/`, `tests/test_conferencias_*`,
    a lista e o relatório;
  - D-767, D-785, D-786, D-787 e D-797: cumpridas.

## Achados

Os números começam com "N" para não se confundir com os 19 do primeiro relatório.

1. **N1, grave: o "sim" do Samuel é forjável, e isso reabre os achados 6 e 7.** `problema_do_sim`
   (`regras_dos_agentes/excecoes.py:135`) aceita qualquer pedaço que exista na linha da decisão
   (`regras_dos_agentes/livro.py:51`).
   - Provado na cópia: com o erro novo `return ["schtasks", "/Run", "/TN", "nova"]` em `atualizacao.py` e o item na
     lista com `"sim": {"decisao": "D-791", "em": "19/11/2026", "palavras": "sim"}`, o gancho dá código 0, e
     `protecao.comparar` não acha nada.
   - `"palavras": "a"` também passa.
   - Destino: consertar. O item novo só passa se a linha da decisão citada no Livro nomear aquele lugar, com o arquivo
     e o texto achado. Para a lista inteira valer, a decisão tem de ser a que registra o "sim" à lista, com um tamanho
     mínimo de palavras. A outra saída: o item novo nunca passa por máquina, só pela gerente, conferido pela K17.
2. **N2, médio: chamadas por apelido de biblioteca do Windows não são barradas, e isso não está escrito.**
   (`regras_dos_agentes/porteiro.py:194`).
   - A biblioteca é devolvida e usada fora da função (`teste_velocidade.py:1746`).
   - Também passam `ctypes.CDLL` e `ctypes.cdll`, `getattr(ctypes, ...)` e `creationflags=f` (com o número numa
     variável).
   - Destino: consertar (seguir o apelido dentro da função pela árvore do código e acrescentar `CDLL`/`cdll`), ou ao
     menos escrever na ressalva e no texto para o Samuel.
3. **N3, médio: afrouxar a busca pelo uso não é protegido, e 8 grupos de palavras não têm exemplo nos testes.**
   - Provado: com a linha de `regras_dos_agentes/porteiro.py:199` trocada para deixar o `msiexec` de fora, a proteção
     não acusa nada. Quem pega é o teste de exemplo.
   - Grupos sem exemplo: `os.popen`, `Start-Process`, `Schedule.Service`, `Update.exe`, WMI e COM (`wmic`, `win32com`,
     `comtypes`...), pywin32, `oledll`, e as outras configurações (`bcdedit`, `rundll32`...).
   - Pelo vizinho, ainda passam: `["sc", "create"]`, `net stop`, `taskkill`, `Stop-Process`,
     `New-Object -ComObject WScript.Shell` e `Get-PhysicalDisk`.
   - Destino: consertar. Um exemplo errado nos testes para cada palavra da busca (assim afrouxar pelo uso faz um teste
     falhar), e as palavras vizinhas acrescentadas. Acrescentar é seguro e não tira nada da lista, mas pode aumentar a
     conta: se aumentar, a lista é refeita antes do "sim".
4. **N4, baixo: o rótulo de pronto vale numa pasta `quem-quebrou/` de outro trabalho, ou em `relatorios/quem-quebrou/`
   direto** (`regras_dos_agentes/porteiro_mudancas.py:74`). Provado: só aviso K14. Destino: consertar (só a pasta
   `quem-quebrou/` do próprio trabalho vale), ou acrescentar à ressalva da imitação.
5. **N5, baixo: falsos alarmes possíveis** (`regras_dos_agentes/porteiro.py:199`). `creationflags=0` conta como
   conversa com o Windows, e "self-service" e "hku:" num texto também. Hoje nenhum aparece no programa. Destino: não é
   defeito agora; escrever na ressalva.
6. **N6, médio: o texto para o Samuel ainda não segue o §11.13 em três pontos**
   (`relatorios/passo0-2026-11-19/lista-de-excecoes-para-o-samuel.md:18`).
   - A imagem é o próprio texto, sem print do caso real (regra 3).
   - "Os 5 lugares" e "a conta dá 6" confundem.
   - Os 16 lugares do teste de velocidade entram na pergunta nova, mas a D-800 já mandou para depois "o teste de
     velocidade lendo placa de vídeo e disco pelo PowerShell". A linha `teste_velocidade.py:428` (`Get-CimInstance
     Win32_VideoController`) é essa mesma leitura e ficou "fora do plano, a perguntar". O mesmo caso na régua dos
     filtros foi tratado como "mesmo pedaço" e foi para depois. É regra 10: não perguntar de novo o que já foi
     respondido.
   - Destino: consertar. Classificar a linha da placa de vídeo pelo mesmo critério da régua dos filtros, pôr um print
     do caso real e dizer "6 lugares" no título.
7. **N7, baixo: a correção 3 ainda cega a busca num f-string visível que tenha `{}` e `/* */`**
   (`regras_dos_agentes/leitura_do_codigo.py:130`). Provado com `f"Arquivo {nome} salvo /* conforme D-731 */"`. Na
   prática é raro. Destino: escrever na ressalva, ou exigir cara de folha de estilo mais forte (um seletor seguido de
   `{`).
8. **N8, baixo: o arquivo novo só ganha as regras de Windows se o título do pedido tiver "Windows", "instalador" ou
   "atualiza"** (`regras_dos_agentes/tabela_arquivos.py:149`). Os títulos "desinstalar limpo", "publicar" e "pasta
   segura" não ganham. Destino: escrever no pacote que a gerente põe "Windows" no título ou uma linha na tabela, ou
   ampliar a busca do título.
9. **N9, baixo: o pacote que confere o formulário deste passo foi feito por quem construiu**
   (`relatorios/passo0-2026-11-19/anexos/pacote-passo0.md:10`). Destino: não é defeito, é o caso de partida. A gerente
   confirma que é o pedido dela antes de usar.

## Para a gerente: o que ficou fora do projeto

Na cópia temporária da sessão (`C:\Users\fotog\AppData\Local\Temp\claude\b9ca076ad002e817\848d7b72-406b-4bfe-aabf-f5b3005d7b22\scratchpad\quebrar\copia`),
ficaram mais estes ramos de prova: `prova2-sim`, `prova2-k10`, `prova2-k13`, `prova2-prot`, `prova2-prot2`,
`prova2-prot3`, `prova2-gancho` e `prova2-ligar`. Ficaram também os pacotes `pac-impl.md` e `pac-lay.md` e o script
`recontar2.py`. Nada foi apagado.
