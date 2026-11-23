# ONDE-PAREI — a primeira trava do atualizador novo (23/11/2026)

Implementador. Ramo `atualizador-novo-2026-11-23` (saiu de `obra-2026-10-26` em `c8531595`), worktree
`.claude/worktrees/atualizador-novo`. Pedido da gerente de 23/11/2026.

**Situação: feito, esperando a gerente.** O teste está em `tests/test_trava_windows.py`. A trava falha hoje de
propósito, com 62 lugares. As 11 provas de que ela funciona passam.

## Decisões que esta tarefa precisa cumprir

- **D-830 (23/11/2026):** "refazer". E a mensagem do Fable que o Samuel colou: "ela pode mandar escrever a primeira trava
  (o teste que diz 'só core/windows.py fala com o Windows'). Esse teste vai falhar hoje de propósito — a lista do que
  falha é a lista de trabalho do atualizador novo". Pela resposta do Fable, a trava é um "Teste de AST em `tests/`:
  `ctypes`, `subprocess`, `winreg`, `os.startfile` importados somente em `core/windows.py`. Binário, sem lista de
  exceções."
- **D-765 (17/11):** "eu não quero fazer nenhum conserto até o .exe estar pronto para o kaique [...]". Nenhuma linha do
  programa muda nesta tarefa.
- **D-791 / D-801 / D-802:** a lista de exceções do porteiro só ganha item com o "sim" dele. Esta tarefa não põe item
  nela.
- **D-605 (§11.8):** "nenhuma função nova [...] pode alterar o que já está escolhido e testado". Nenhum teste antigo foi
  mudado, e nenhum teste antigo quebra.
- **§11.12 (uma peça só):** a trava não pode virar uma segunda conferência da mesma regra ao lado da K01.
- **D-809:** nenhum comando que mude o `.git` inteiro. O teste só lê a lista do git (`git ls-files`), pela peça única
  do git.
- **D-793 / §11.11:** não abri outro agente.

## O que já está escolhido e testado aqui

- O porteiro (`regras_dos_agentes/porteiro.py`). A K01 procura a conversa com o Windows por palavras
  (`PALAVRAS_DO_WINDOWS`, PROTEGIDA "nao_some" em `protecao.py`). A definição de programa é `e_programa`, com
  `NAO_E_PROGRAMA` PROTEGIDA "igual". A peça única é `PECA_UNICA_DO_WINDOWS`.
- `tests/test_conferencias_*.py`: as provas do porteiro. Entre elas, `test_o_repositorio_so_tem_os_erros_que_a_lista_deixa`,
  que barra qualquer achado fora da lista "valendo". Esses arquivos estão em `porteiro_mudancas.PROTEGIDOS` (K17): só a
  gerente os muda.
- O juiz do GitHub (`juiz.py`) julga o ramo com o porteiro e a lista **da versão de teste**, não com os do ramo.

## A escolha: teste à parte, e não uma conferência dentro do porteiro

**Escolhi um teste à parte, `tests/test_trava_windows.py`. Quando for juntado, ele deve substituir a parte da K01 que
procura as mesmas coisas por palavras.** Os motivos:

1. **Pôr a regra dentro do porteiro quebraria um teste antigo.** A lista de exceções está "valendo". Uma conferência
   nova (K26, ou uma K01 que lê a estrutura) acharia os 62 lugares. Nenhum deles está na lista com essa conferência,
   então `test_o_repositorio_so_tem_os_erros_que_a_lista_deixa` passaria a falhar. Para ele voltar a passar, seria
   preciso pôr 62 itens na lista, o que exige o "sim" do Samuel (D-791) e foi proibido no pedido.
2. **O juiz do GitHub nem veria a conferência nova.** Ele usa o porteiro da versão de teste. Uma K26 feita neste ramo só
   valeria depois que a gerente a juntasse.
3. **Trocar a K01 por uma versão que lê a estrutura afrouxa a proteção.** Tirar linhas de `PALAVRAS_DO_WINDOWS` (o
   `winreg`, o `os.startfile`, o `windll`) é barrado por `protecao.py` ("nao_some") e pela K17. Não contornei. É mudança
   da gerente, com o "sim" do Samuel.
4. **Uma peça só, sem definição copiada.** O teste não tem definição própria de "programa" nem de "peça única". Ele
   importa `porteiro.e_programa` e `porteiro.PECA_UNICA_DO_WINDOWS`, lê o código com `leitura_do_codigo.arvore`, que é a
   mesma leitura do porteiro, e pega a lista dos arquivos com `conversa_com_o_git.arquivos_do_git`.
   **A sobreposição que existe hoje:** a K01 acusa por palavra `winreg`, `os.startfile`, `windll`/`WinDLL`/`CDLL` de DLL
   do Windows e o apelido da biblioteca. A trava acusa por estrutura o `import` de `ctypes`, `subprocess`, `winreg` e o
   uso de `startfile`. São duas conferências da mesma regra até a gerente decidir. Sugestão para quando juntar: a parte
   de imports, `winreg` e `startfile` da K01 sai, e fica a trava. As palavras do PowerShell, do `schtasks`, do `icacls`
   etc. continuam na K01 até virarem a segunda trava do Fable ("nenhum literal de string fora de `core/windows.py`
   contém `powershell`, `-Command` ou `.ps1`").

## Como fica para quem usa e no livro

Nada muda para o Kaique nem no PDF. Nenhuma linha do programa mudou, só um teste novo em `tests/`. O que muda é a rodada
do GitHub: **ela vai falhar enquanto houver lugar na lista**. Isso é de propósito (D-830), mas tem consequência. Veja as
ressalvas.

## Caminho → função (§11.12)

| Caminho | O que usa |
|---|---|
| o teste da trava (repositório inteiro) | `falhas_do_repositorio` → `falhas_nos_arquivos` → `lugares_proibidos` |
| as provas com arquivo de exemplo | `falhas_nos_arquivos` → `lugares_proibidos` (a mesma conta, sem ler o disco) |
| o que é programa | `porteiro.e_programa` (`NAO_E_PROGRAMA`), o mesmo do porteiro |
| a peça única | `porteiro.PECA_UNICA_DO_WINDOWS` |
| ler o código | `leitura_do_codigo.arvore`, a mesma do porteiro (aceita a marca de UTF-8 e levanta `CodigoIlegivel`) |
| a lista dos arquivos | `conversa_com_o_git.arquivos_do_git` (`git ls-files`, só lê), o mesmo de `porteiro.achados_do_repositorio` |

## O que pode falhar, e o que a trava faz em cada caso

- **Arquivo do programa que não abre ou não é texto UTF-8:** vira falha `arquivo:0: não deu para ler`. Nunca passa.
- **Código que o Python 3.14 não consegue ler:** vira falha `arquivo:0: o código não pôde ser lido`.
- **O git não responde:** `GitFalhou` sobe e o teste falha com o motivo. Nunca passa calado.
- **Comentário ou docstring que fala de `ctypes`:** não conta. Não é árvore de código. Tem prova.
- **O `.ctypes` de uma imagem do numpy** (`imagem.ctypes.data_as`, usado para entregar a imagem à DLL do ScanTailor):
  não é o módulo. Não conta sozinho, mas o `import ctypes` do mesmo arquivo é acusado, então nada fica escondido. Tem
  prova. Na primeira versão da trava eu contava esse `.ctypes`. Ela deu 80 lugares, 18 deles esse alarme falso, e
  estreitei a regra: só conta o módulo pego dentro de outro módulo importado no arquivo (`windows.subprocess`).

## A peça de fora usada: o `ast` do Python (§11.12.6)

Fonte: https://docs.python.org/3/library/ast.html (Python 3.14).
- `ast.Import`: `names` é uma lista de `alias(name, asname)`, e `name` traz o nome com ponto (`ctypes.wintypes`).
- `ast.ImportFrom`: tem `module` (None em `from . import x`), `names` e `level` (0 = absoluto; 1 ou mais = relativo).
- `ast.Call`: `func` e `args`. `ast.Attribute`: `value` e `attr`. `ast.walk` passa por todos os nós e não segue ordem.
  Por isso o resultado é ordenado no fim.
- Comentário não vira nó. Docstring é um `ast.Constant` e só conta se estiver numa das formas acima, o que não acontece.
- `__import__` (https://docs.python.org/3/library/functions.html#import__) e `importlib.import_module`
  (https://docs.python.org/3/library/importlib.html) recebem o nome do módulo como texto. Só o texto escrito por inteiro
  é lido.
- `os.startfile` só existe no Windows (https://docs.python.org/3/library/os.html#os.startfile) e está em `os.__all__`
  lá. Por isso `from os import *` é acusado.

## A prova de que a trava funciona

Rodei `D:\programas\EditorImpressao\.venv\Scripts\python.exe -m pytest tests\test_trava_windows.py -q` em 23/11/2026.
Resultado: **1 failed, 11 passed**.
- **Falha hoje:** `test_so_core_windows_fala_com_o_windows` acusa 62 lugares (a lista abaixo).
- **Acusa fora da peça e não acusa dentro:** `test_acusa_import_ctypes_fora_da_peca_e_nao_acusa_dentro` usa um arquivo
  de exemplo com `import ctypes`. Em `atualizacao.py` e em `core/qualquer.py` ele é acusado. O mesmo texto em
  `core/windows.py` dá zero.
- `test_usa_a_definicao_de_programa_do_porteiro`: o que está em `tests/`, `relatorios/`, `regras_dos_agentes/` e `docs/`
  não é acusado. Pasta nova e `.pyw` são acusados.
- `test_acusa_cada_jeito_de_importar_e_de_usar`: os 12 jeitos de importar ou usar, uma linha cada.
- `test_acusa_from_os_import_estrela_que_traz_o_startfile`, `test_o_ctypes_de_uma_imagem_do_numpy_...`,
  `test_nao_acusa_comentario_docstring_texto_nem_nome_parecido`,
  `test_codigo_ilegivel_e_arquivo_que_nao_abre_sao_falha_nunca_passou` e `test_cada_modulo_proibido_e_acusado` (4
  módulos).
- O porteiro rodado no próprio `tests/test_trava_windows.py` dá zero achados. O arquivo não tem comando do git (K25) e
  todas as funções têm docstring (K12).
- Não mexi no porteiro, então `tests\test_conferencias_codigo.py` não precisou rodar.

## A lista do que falha hoje (62 lugares, arquivo:linha)

### (a) Conversa com o Windows de verdade

**(a1) O atualizador e os testes à distância: a lista de trabalho do atualizador novo (10)**
- `atualizacao.py:114` `import subprocess`. Usado no `Update.exe apply` (L671), no PowerShell (L965), nos comandos do
  Windows de `_rodar` (L789) e no teste rápido, que roda o nosso próprio exe (L632).
- `atualizacao.py:432`, `:433` `ctypes`/`wintypes`: `GetNamedSecurityInfoW`, o dono do arquivo.
- `atualizacao.py:750` `ctypes`: `CreateMutexW`, a marca de "programa aberto".
- `atualizacao.py:759` `ctypes`: `OpenMutexW`, para conferir a marca.
- `atualizacao.py:1194` `winreg`: o Visual C++ está instalado?
- `atualizacao.py:1279` `winreg`: a chave do instalador antigo (Inno).
- `core/_testes_a_distancia_windows.py:32`, `:34`, `:36`: `ShellExecuteExW` "runas", PowerShell e `schtasks`.

**(a2) Windows de verdade em outras partes. Não é do atualizador; estão na lista de exceções como "depois da entrega"
(D-800/D-802) (24)**
- `avaliar.py:26`, `:1655`: `SHGetFolderPathW`, onde fica a Área de Trabalho (régua dos filtros).
- `core/nucleos.py:44`: `GlobalMemoryStatusEx`, a memória livre.
- `historico.py:7`, `:199`, `:212`: abrir a pasta no Explorer (`explorer /select`, `os.startfile`) e imprimir
  (`os.startfile(..., "print")`).
- `teste_velocidade.py:75` (PowerShell), `:362`, `:432` (`winreg`: placa de vídeo, processador), `:476`, `:641`,
  `:642`, `:1676`, `:1736`, `:1737`, `:1755`, `:1756`, `:1903`, `:1904`, `:1918`, `:1919`, `:2230`, `:2250`
  (`kernel32`/`user32`/`psapi`: memória, não dormir, janela preta, console).
- `ui/brasao_girando.py:223`: `OpenProcess`/`WaitForSingleObject`, o programa continua aberto?

### (b) Não é o Windows: DLL nossa, processo nosso, ferramenta de montar (27)

**DLL nossa do ScanTailor (`core/nativo/st_ferramentas.dll`, `st_gravura.dll`) (10).** Sugestão: uma peça única das
nossas DLLs. Hoje duas carregam a DLL, `core/st_ferramentas.py:315` e `core/gravura_scantailor.py:169`, cada uma com o
seu `CDLL` e o seu `add_dll_directory`. As outras só usam os tipos do `ctypes`.
- `core/caixas_scantailor.py:82`, `core/cores_scantailor.py:52`, `core/desentortar_scantailor.py:69`,
  `core/dividir_scantailor.py:45`, `core/endireitar_scantailor.py:62`, `core/gravura_scantailor.py:47`,
  `core/luz_scantailor.py:46`, `core/pontinhos_scantailor.py:63`, `core/preto_e_branco_scantailor.py:60`,
  `core/st_ferramentas.py:43`.

**Processo nosso (5).** Sugestão: uma peça única para abrir os nossos processos. `core/ocr_comum.abrir_processo` já
faz isso para os OCRs.
- `core/ocr_comum.py:39`: `abrir_processo`, o `Popen` dos OCRs.
- `core/ocr_kraken.py:89`: o motor do Kraken, com `PIPE` e `TimeoutExpired`.
- `core/ocr_tesseract.py:87`: `tesseract.exe --version` e `_matar`.
- `core/paginas_em_outro_processo.py:64`: o servidor de páginas.
- `ui/tela_de_carregamento.py:38`: o brasão em outro processo (`abrir=subprocess.Popen`).

**Ferramentas de montar, publicar e testar, que ficam na raiz e não vão no programa do Kaique (8).** Sugestão:
decidir se esses scripts são "programa" para a trava. Hoje são, pela definição do porteiro.
- `compilar_detector_gravura.py:42`, `compilar_st_ferramentas.py:44`: o `cmake`.
- `empacotar.py:115`: o PyInstaller e o compilador do Inno.
- `empacotar_teste_velocidade.py:68`: o PyInstaller.
- `montar_motor_kraken.py:98`: o `python`/`pip` do motor.
- `gerar_prints.py:15`: roda a si mesmo.
- `teste_completo.py:326`: roda `teste_robustez_completo.py`.
- `avaliar.py:31`: roda `python -c` para medir a abertura.

**Import que não conversa com nada (4).** Sugestão: tirar o import, quando a D-765 deixar mexer.
- `conferencia.py:71`: só `subprocess.list2cmdline`, que monta um texto.
- `publicar_versao_kaique.py:70`: só o tipo `CompletedProcess`. O `gh` roda por outra peça.
- `teste_bateria.py:15`, `teste_robustez.py:12`: `import ctypes` sobrando, que nem é usado. A docstring diz que trocou
  para o `psutil`.

### (c) Dúvida (1)

- `core/ocr_comum.py:209`: chama o Windows de verdade (`kernel32.SetDllDirectoryW`), mas só para o OCR que roda à
  parte não herdar a pasta de DLLs do programa. É Windows, então iria para `core/windows.py`. Mas faz parte de "abrir um
  processo nosso", então iria para a peça dos processos. Precisa de decisão de desenho.

**Conta, conferida com a saída do teste linha por linha:** 10 (a1) + 24 (a2: 2 + 1 + 3 + 17 + 1) + 27 (b: 10 + 5 + 8 +
4) + 1 (c) = 62. Nenhuma linha se repete. O `core/ocr_comum.py` tem duas linhas: a 39 está em (b) e a 209 em (c).

## A mesma lista separada pela sugestão do Fable (recado da gerente, 23/11; ainda não é decisão do Livro)

A sugestão:
- **Proibido fora de `core/windows.py`:** `ctypes.windll`, `ctypes.WinDLL`, `wintypes`, `winreg`, `os.startfile`.
- **Permitido em qualquer lugar:** `ctypes.CDLL` carregando as DLLs de `core/nativo/`.
- **`subprocess`:** só numa lista fixa de arquivos: `core/windows.py`, o servidor de páginas, o lançador do Kraken e
  `empacotar.py`.

Não mudei a trava: ela continua como o pedido manda. Abaixo está só a separação. Conferi os lugares de uso lendo a
árvore de cada arquivo, não só a linha do `import`.

### Proibido, fora do atualizador (grupo à parte: não muda nada nelas)

- `core/nucleos.py:78`: `ctypes.windll.kernel32.GlobalMemoryStatusEx`, que lê a memória livre para decidir quantas
  páginas trabalham ao mesmo tempo. O import está na linha 44.
- `core/ocr_comum.py:211`: `ctypes.WinDLL("kernel32")`, `GetDllDirectoryW`/`SetDllDirectoryW`. Por um instante, tira a
  pasta de DLLs do programa para o OCR que roda à parte não herdá-la. O import está na linha 209.
- `historico.py:199`: `os.startfile(pasta)`, que abre a pasta no Explorer.
- `historico.py:212`: `os.startfile(caminho, "print")`, que manda imprimir pelo Windows.
- `avaliar.py:1655` e `:1659`: `windll`/`wintypes` e `SHGetFolderPathW`, que pergunta onde fica a Área de Trabalho
  (régua dos filtros). O `import ctypes` está na linha 26.
- `ui/brasao_girando.py:225`: `ctypes.windll.kernel32` `OpenProcess`/`WaitForSingleObject`, que confere se o programa
  continua aberto enquanto o brasão gira.
- `teste_velocidade.py`, 17 lugares de import e o uso deles:
  - `winreg` nas linhas 362 e 432 (a placa de vídeo e o processador);
  - `windll` nas linhas 479, 1678 e 2233 (a memória, "não dormir" e a lista de processos do console);
  - `WinDLL`/`wintypes` nas linhas 642 a 664, 1737 a 1759, 1904 a 1922 e 2250 a 2254 (a memória do processo, a janela
    preta e a classe da janela).

### Proibido, no atualizador e nos testes à distância (a lista de trabalho do atualizador novo)

- `atualizacao.py`:
  - `wintypes` nas linhas 433, 438 e 441;
  - `windll` nas linhas 435, 752 e 761;
  - `winreg` nas linhas 1194 e 1279.
- `core/_testes_a_distancia_windows.py`: `wintypes` nas linhas 36 e 63 a 77; `windll` nas linhas 94 a 99.

### Permitido pela sugestão

- `ctypes.CDLL` das DLLs nossas: `core/gravura_scantailor.py:169` e `core/st_ferramentas.py:315`.
- `subprocess` nos arquivos da lista: `core/paginas_em_outro_processo.py:64`, `empacotar.py:115` e, se "o lançador do
  Kraken" for `core/ocr_kraken.py`, o `:89` (ver "o que cai fora" abaixo).

### `subprocess` fora da lista de arquivos: falharia pela sugestão (16)

- **Atualizador e testes à distância:** `atualizacao.py:114` e `core/_testes_a_distancia_windows.py:34`.
- **Outras partes do programa:**
  - `core/ocr_comum.py:39`: o `abrir_processo` dos OCRs, por onde o Kraken abre de verdade;
  - `core/ocr_tesseract.py:87`: o `tesseract.exe`;
  - `historico.py:7`: o `explorer /select`;
  - `ui/tela_de_carregamento.py:38`: o brasão;
  - `teste_velocidade.py:75`: o PowerShell.
- **Scripts de apoio:**
  - `avaliar.py:31`;
  - `compilar_detector_gravura.py:42` e `compilar_st_ferramentas.py:44`;
  - `empacotar_teste_velocidade.py:68`;
  - `montar_motor_kraken.py:98`;
  - `gerar_prints.py:15`;
  - `teste_completo.py:326`;
  - `conferencia.py:71`: só `list2cmdline`;
  - `publicar_versao_kaique.py:70`: só o tipo.

### O que cai fora da sugestão (ela não diz o que fazer)

1. **"O lançador do Kraken" não é um arquivo só.** O `Popen` de verdade está em `core/ocr_comum.py`
   (`abrir_processo`, L185-219), que também abre o `tesseract.exe`. O `core/ocr_kraken.py` usa o `subprocess` para
   `PIPE`, `TimeoutExpired` e o tipo. Pela sugestão ao pé da letra, um dos dois falha, ou os dois entram na lista.
2. **O `import ctypes` só para os tipos** (`c_double`, `c_void_p`, `create_string_buffer`) nos 8 arquivos
   `core/*_scantailor.py` que chamam a DLL nossa sem carregá-la: caixas, cores, desentortar, dividir, endireitar, luz,
   pontinhos e preto e branco. A sugestão não proíbe nem permite. Pela letra dela, passam, porque não usam `windll`,
   `WinDLL` nem `wintypes`.
3. **`import ctypes` sobrando**, sem uso nenhum: `teste_bateria.py:15` e `teste_robustez.py:12`. Pela letra, passam.
4. **"CDLL carregando as DLLs de `core/nativo/`" não se confere lendo o código.** O caminho vem de uma variável
   (`ctypes.CDLL(str(self.caminho))`). Uma trava que lê a estrutura não sabe se o caminho é de `core/nativo/`. Ou ela
   aceita todo `CDLL`, e aí `CDLL("kernel32")` passa, ou só aceita o `CDLL` nos dois arquivos, o que já é uma lista de
   arquivos.
5. **Jeitos de falar com o sistema que a sugestão não lista:** `ctypes.oledll`, `ctypes.cdll.kernel32` e
   `ctypes.CDLL("kernel32")` (a K01 pega por palavra), além de `os.system`, `os.popen` e `os.spawn*`.
6. **A lista fixa de arquivos para o `subprocess`** é uma lista de lugares permitidos. Isso não bate com o "binário,
   sem lista de exceções" da primeira mensagem do Fable. Ela pode ser lida como "as peças únicas de cada coisa", desde
   que cada arquivo da lista tenha um papel escrito. Isso é decisão, não minha.
7. **Os scripts de montar** (`compilar_*`, `montar_motor_kraken.py`, `empacotar_teste_velocidade.py`) rodam `cmake`,
   PyInstaller e `pip`. A sugestão só põe o `empacotar.py` na lista. Pela letra, os outros falham.

## Perguntas para o Samuel

(A gerente adapta para a Central. Não há print, porque nada na tela muda: é uma conferência do código.)

**1. Os pedaços do programa que conversam com outras coisas que não são o Windows (grupo b).**
- *Do que se trata:* a trava nova diz "só um arquivo do programa pode rodar outro programa ou carregar uma DLL". Ela
  acusa 27 lugares que não conversam com o Windows: as ferramentas do ScanTailor que viraram DLL nossa, o leitor de
  texto (OCR) e o servidor de páginas, que rodam à parte, e os scripts de montar o instalador.
- *O que acontece hoje:* cada um faz isso por conta própria. Isso não é defeito que o Kaique vê; é jeito de escrever o
  código.
- *O que você escolhe:*
  - (1) Tudo vai para o mesmo arquivo do Windows. É simples, mas mistura as ferramentas do ScanTailor com o Windows.
  - (2) **Sugestão do implementador:** um arquivo só para as DLLs nossas e um arquivo só para os programas nossos que
    rodam à parte. A trava diz qual dos três arquivos pode fazer cada coisa e continua sem lista de exceções. Os
    scripts de montar o instalador ficam de fora da trava, porque não vão para o Kaique.
  - (3) Só comentário.
- *O que muda no que já funciona:* nada agora. A mudança só aconteceria depois da entrega ao Kaique (D-765), e o
  programa faria o mesmo de antes.

## Ressalvas

- **A rodada do GitHub vai falhar por causa deste teste**, de propósito (D-830). Enquanto ele estiver no ramo, a
  rodada inteira sai vermelha, e uma falha nova de outro teste fica misturada com esta. Sugestão técnica para a
  gerente: na hora de juntar, decidir se ele entra como `xfail(strict=True)` até o atualizador novo ficar pronto ou se
  fica falhando. Não fiz isso por conta própria: o pedido diz "vai falhar hoje de propósito".
- **Não disparei a rodada do GitHub.** O pedido manda rodar só o arquivo novo e fazer commit com `[skip ci]`. Por
  isso não há número de rodada.
- **O que a trava não pega:** `os.system`, `os.popen`, `os.spawn*`, `os.exec*`, `multiprocessing`,
  `asyncio.create_subprocess_*`, `sys.modules["ctypes"]`, o nome montado em pedaços (`__import__("ct" + "ypes")`) e um
  módulo nosso que guarda o `subprocess` com outro nome e o devolve por uma função. Está escrito na docstring do teste.
  A K01 pega `os.system` e `os.popen` por palavra.
- **A sobreposição com a K01** continua até a gerente juntar e decidir. Ver "A escolha".
- Rodei o teste no PC. Ele só lê arquivos. Nenhuma janela abriu e nada do Windows foi mexido.

## Ideias para a Lista de espera

- Duas peças carregam a mesma DLL do ScanTailor (`core/st_ferramentas.py:315` e `core/gravura_scantailor.py:169`), cada
  uma com o seu `CDLL` e o seu `add_dll_directory`. É uma regra em dois lugares (§11.12).
- A trava poderia pegar também `os.system`, `os.popen` e `os.spawn*`, para a regra "rodar outro programa" ficar inteira.
  Não estava no pedido do Fable.

## Bugs para a Lista de bugs

- 23/11/2026, `teste_bateria.py:15` e `teste_robustez.py:12`: `import ctypes` que não é usado (sobrou da troca para o
  `psutil`). Não impede nada.

## Commits

- `tests/test_trava_windows.py` e este ONDE-PAREI. O commit está no fim da entrega.
