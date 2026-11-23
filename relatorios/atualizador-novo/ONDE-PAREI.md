# ONDE-PAREI — a trava dos donos, terceira volta (23/11/2026)

Implementador. Ramo `atualizador-novo-2026-11-23`, worktree `.claude/worktrees/atualizador-novo`, a partir de
`d792ebfc`. Pedido da gerente de 23/11/2026, com a revisão do Fable aos 5 pontos que não fechavam na segunda volta.

**Situação: a terceira volta está feita e esperando a gerente.** A trava passa hoje, pela catraca: 46 lugares
congelados, `TETO = 46`. Rodei `D:\programas\EditorImpressao\.venv\Scripts\python.exe -m pytest tests\test_trava_windows.py -q`:
**40 passed, 3 skipped** (as três pendências paradas). Só mudaram `tests/test_trava_windows.py` e este arquivo. As voltas
anteriores ficam abaixo, como estavam.

## Decisões que esta tarefa precisa cumprir

- **D-830 (23/11/2026):** "refazer", e a trava do Fable: cada capacidade só no seu dono, "binário, sem lista de
  exceções". Nesta volta: a catraca no lugar do `xfail`, o mapa final, os nomes proibidos ao dono das DLLs e as raízes.
- **D-765:** nenhuma linha do programa muda. Não mudou: só o teste e o ONDE-PAREI.
- **§11.8 / D-605:** nenhum teste antigo muda. Nenhum teste de fora deste arquivo foi tocado (ver a ressalva 6 sobre as
  provas da segunda volta, que são deste mesmo arquivo novo).
- **D-809:** nada de comando que mude o `.git` inteiro. Só `git ls-files` pela peça do git, e `git add`/`commit`/`push`.
- **D-793 / §11.11:** não abri outro agente. Não abri janela nem rodei o programa.
- **Do pedido:** nada no porteiro e nada no `empacotar.py`.

## Como cumpri cada uma

- D-830: a trava é binária para lugar novo (falha na hora) e sem lista de exceções que cresça (a lista congelada só
  diminui, com teto). Provas na seção "As provas".
- D-765, porteiro, `empacotar.py`: `git diff --stat` mostra só `tests/test_trava_windows.py` e este arquivo.
- §11.8: nenhum arquivo de teste além deste foi aberto para escrita.
- D-809 / D-793: só os comandos acima; nenhum agente aberto.

## O que já está escolhido e testado aqui

- A primeira e a segunda volta deste mesmo teste (só neste ramo). O desenho dos donos da segunda volta continua; o mapa
  mudou pelo pedido (o `subprocess` agora tem dois donos).
- O porteiro e a lista de exceções (`regras_dos_agentes/`): não mexi. O porteiro (`conferir_codigo`) rodado no arquivo
  novo dá 0 achados.

## Como fica para quem usa e no livro

Nada muda para o Kaique nem no PDF: nenhuma linha do programa mudou. O que muda é a rodada do GitHub: a trava agora
passa (sem `xfail`) e fica vermelha na hora em que alguém usar uma capacidade num lugar novo fora do dono, ou quando
um lugar da lista for consertado sem tirar a linha.

## O que mudou no teste

1. **Catraca no lugar do `xfail`.** A marca saiu. `LISTA_CONGELADA` tem os 46 lugares de hoje, um por linha, separados
   em grupos com comentário. `conferir_a_catraca` cobra:
   - **lugar novo:** chave acusada que não está na lista falha na hora ("LUGAR NOVO ...", com a linha onde está);
   - **lugar perdoado à toa:** chave da lista que não é mais acusada falha com "tire esta linha da lista e abaixe o
     teto";
   - **o teto:** `assert len(LISTA_CONGELADA) <= TETO`, `TETO = 46`; e linha repetida na lista também falha.
   - Falha de leitura (raiz que falta, `OCULTOS` ilegível, arquivo que não abre) nunca entra na catraca: sempre falha.
2. **A chave do lugar:** `"arquivo | função onde mora | capacidade | o que foi achado"`, sem o número da linha. Ex.:
   `atualizacao.py | _marca_existe | Windows pelo ctypes | usa ...windll`. A função vem da peça de leitura do porteiro
   (`leitura.funcao_em_volta`, com a classe na frente: `BibliotecaScanTailor._carregar`); fora de função, `(fora de
   função)`. **Por quê:** escrever código acima não muda nenhuma das quatro partes (tem prova: dez linhas novas acima,
   mesma chave, linha diferente). Quando o lugar muda de verdade (outra função, outro jeito de importar, outra
   capacidade), a chave muda, e a catraca acusa um novo e um que sumiu, que é o certo. O mesmo jeito repetido na mesma
   função é um lugar só (os doze `wintypes.DWORD` do corpo de `core/_testes_a_distancia_windows.py` são uma linha).
3. **Mapa final dos donos:** `core/windows.py` → `ctypes` (com "Windows pelo ctypes"), `winreg`, `os.startfile`,
   `subprocess`; `core/nativo_dll.py` → `ctypes` e carregar DLL; `core/processos.py` → `subprocess`. O
   `core/windows.py:91` (`import subprocess`) saiu da lista. O `explorer /select` do `historico.py` continua acusado.
4. **`os.system/popen/spawn*/exec*`:** continuam proibidos em todo lugar, inclusive nos donos. Nada mudou
   (`test_rodar_programa_pelo_os_nao_tem_dono`).
5. **Os nomes do Windows no dono das DLLs:** `windll`, `WinDLL`, `oledll`, `OleDLL`, `wintypes`, `get_last_error`,
   `FormatError`, `GetLastError` viraram a capacidade "Windows pelo ctypes", cujo único dono é `core/windows.py`. São
   acusados como atributo (pelo nome, venha de onde vier: `ctypes.windll`, `kernel32.GetLastError`), como nome importado
   (`from ctypes import windll` e o uso dele), no `import ctypes.wintypes`, no `from ctypes.wintypes import ...` e no
   `getattr(ctypes, "windll")`. Ver o ponto 2 de "O que não fechou": isso vale em todo arquivo, não só no dono das DLLs.
6. **Raízes do fechamento** (`raizes_do_programa`): `main.py`; `motor_kraken/servidor_kraken.py`, procurando os módulos
   na pasta dele (roda com `python -I servidor_kraken.py`, então a pasta do script é onde o Python procura); e os módulos
   nossos da `OCULTOS` do `empacotar.py`.
   - **A `OCULTOS` dá para ler sem rodar:** é `OCULTOS = [...]` no corpo do `empacotar.py` (linha 165), uma lista de
     textos fixos, usada só em `for modulo in OCULTOS: comando += ["--hidden-import", modulo]` (linhas 883-884). Lida
     com `ast.literal_eval`. Se um dia ela for montada por função, ganhar `append`/`+=`, outra atribuição, um
     `--hidden-import` fora do laço, ou aparecer `--collect-submodules`/`--collect-all`/`--hiddenimport`, a leitura
     falha e diz a linha. Módulo que parece nosso (`core.x`) e não tem arquivo também falha. O `empacotar.py` não mudou.
   - Os 8 módulos nossos da `OCULTOS` (`core.gravura_scantailor`, `core.st_ferramentas`, `core.ocr_comum`,
     `core.ocr_doctr`, `core.ocr_tesseract`, `core.ocr_kraken`, `core.ocr_comparar`, `core.ocr_diagnostico`) já estavam
     no fechamento do `main.py`. Os de fora (`doxapy`, `skimage.filters`, `PIL._tkinter_finder`, `onnxtr...`) ficam fora.
   - O fechamento passou de 121 para 122 arquivos: entrou só o `motor_kraken/servidor_kraken.py`.
   - **O motor do Kraken não usa nenhuma das capacidades** (nenhum lugar acusado nele). Ele só importa a biblioteca do
     Python, o numpy, o PIL, o kraken, o torch e o psutil. Não inventei dono.
7. **As duas pendências do `subprocess`**, paradas enquanto `core/processos.py` não existir (como a do `CDLL`):
   `test_pendencia_a_peca_do_windows_so_lanca_programa_da_pasta_do_windows` e
   `test_pendencia_a_peca_dos_processos_recusa_programa_da_pasta_do_windows`. Ver o ponto 1 de "O que não fechou".

## A contagem nova: 46 lugares, TETO = 46

- **(a1) Atualizador e testes à distância: 20.** `atualizacao.py` 12 (o `import subprocess`; `_dono_do_arquivo` 5;
  `marcar_programa_aberto` 2; `_marca_existe` 2; `_ler_versao_do_visual_c` e `_ler_chave_do_inno`, o `winreg`);
  `core/_testes_a_distancia_windows.py` 8 (5 no corpo do arquivo, 3 em `_rodar_elevado`, entre eles o `get_last_error`).
- **(a2) Windows de verdade em outras partes: 9.** `core/nucleos.py` 2, `core/ocr_comum.py` (`abrir_processo`) 2,
  `historico.py` 3 (o `explorer /select` e os dois `os.startfile`), `ui/brasao_girando.py` 2.
- **(b) As nossas DLLs: 12.** Os 10 `import ctypes` e os 2 `CDLL`.
- **(b) Os nossos processos: 5.** `core/ocr_comum.py`, `core/ocr_kraken.py`, `core/ocr_tesseract.py`,
  `core/paginas_em_outro_processo.py`, `ui/tela_de_carregamento.py`.
- Diferença para a segunda volta (34): sai o `core/windows.py:91` (−1); a contagem agora é por chave, e não por linha
  (não muda nada nos 33 que ficam: nenhuma chave deles se repete); e entram 13 chaves de "Windows pelo ctypes" (5 em
  `atualizacao.py`, 5 nos testes à distância, 1 em cada um de `core/nucleos.py`, `core/ocr_comum.py` e
  `ui/brasao_girando.py`). 34 − 1 + 13 = 46. Por linha seriam 61 (os `wintypes` repetidos).

## As provas (40 passam, 3 paradas)

- **Lugar novo falha:** `test_catraca_lugar_novo_falha_na_hora` (sozinho, e ao lado de um da lista). Conferido também no
  repositório de verdade, fora do teste: tirando a primeira linha da lista, a catraca diz "LUGAR NOVO ...
  atualizacao.py | (fora de função) | subprocess | import subprocess [atualizacao.py:114 ...]".
- **Lugar consertado falha pedindo para tirar da lista:** `test_catraca_lugar_consertado_pede_para_tirar_da_lista`.
  No repositório de verdade, com uma linha inventada a mais: "este lugar não é mais acusado: tire esta linha da lista e
  abaixe o teto: ...".
- **O teto:** `test_catraca_a_lista_nunca_passa_do_teto`. No de verdade, com `TETO` 45: "a lista congelada tem 46
  linhas e o TETO é 45: a lista só pode diminuir".
- **A chave não muda com código acima:** `test_catraca_a_chave_nao_muda_quando_se_escreve_codigo_acima`; e
  `test_catraca_o_mesmo_jeito_na_mesma_funcao_e_um_lugar_e_linha_repetida_na_lista_falha`.
- **Nomes proibidos no dono das DLLs:** `test_o_dono_das_dlls_nao_pode_o_windows_pelo_ctypes` (8 casos, um por nome:
  atributo, nome importado e atributo de variável; o mesmo texto em `core/windows.py` dá zero) e
  `test_o_dono_das_dlls_nao_pode_importar_o_wintypes_nem_pegar_por_getattr`.
- **Cada raiz entra no fechamento:** `test_raiz_do_hidden_import_entra_no_fechamento` (um módulo que só a `OCULTOS` põe
  é acusado; sem a raiz, escaparia), `test_raiz_do_motor_do_kraken_procura_na_pasta_dele`,
  `test_a_lista_dos_ocultos_montada_de_outro_jeito_e_falha` (7 jeitos) e `test_cada_raiz_de_verdade_entra_no_fechamento`
  (no repositório de verdade: as raízes lidas sem falha, e cada uma no fechamento).
- As provas da segunda volta continuam, três delas ajustadas ao mapa novo (ressalva 6).

## Caminho → função (§11.12)

| Caminho | O que usa |
|---|---|
| a trava (repositório) | `lugares_do_repositorio` → `raizes_do_programa` + `lugares_da_trava` → `conferir_a_catraca` |
| as provas com arquivos de exemplo | `lugares_da_trava` / `falhas_da_trava` (a mesma conta, sem ler o disco) |
| as raízes | `raizes_do_programa` → `ocultos_do_empacotar` (árvore do `empacotar.py`) |
| o fechamento | `fechamento` → `_indice` (por pasta de busca) → `modulos_pedidos` |
| as capacidades | `_usos_na_arvore` (uma só; `capacidades_usadas` é ela a partir do texto) |
| a função onde mora | `leitura.funcao_em_volta`, a do porteiro |
| ler o código / a lista do git | `leitura.arvore` / `git.arquivos_do_git`, as do porteiro |

## A peça de fora usada (§11.12.6)

- `ast.literal_eval` (https://docs.python.org/3/library/ast.html#ast.literal_eval): avalia só literais (textos, listas,
  tuplas...); com qualquer outra coisa (uma chamada de função, um nome) levanta `ValueError`. É o que transforma
  "lista montada de outro jeito" em falha. Recebe o nó, não o texto.
- `ast.For.iter` e `ast.Name.ctx` (`Load`, `Store`, `Del`): o laço do `--hidden-import` e as escritas na `OCULTOS`.
- O resto do `ast`, como na primeira volta.

## O que não fechou (não ajeitei; para a gerente decidir)

1. **A pendência "a peça do Windows só lança programa da pasta do Windows" não é o que a peça faz hoje.**
   `_caminho_do_programa` (`core/windows.py`, linha 1078) só deixa o caminho como o Windows o completa, para comparar.
   A regra do rodar genérico, `_por_que_recusa` (linha 1195), faz o contrário: recusa o programa da pasta do Windows
   (linha 1245) e deixa rodar os de fora. Hoje quem usa esse caminho para programa de fora: o `vpk`
   (`empacotar.py:1559`) e o `gh` (`publicar_versao_kaique.py:476`), pelo `rodar_em_grupo`; e o `janela_de_prova.py:209`,
   que roda o próprio Python. Os três são scripts, fora do fechamento do programa. **Escolhi parar as duas pendências
   até `core/processos.py` existir**, porque só então os de fora têm para onde ir. Se a gerente quiser outro momento,
   é uma linha em cada pendência. Também fica para decidir se o `vpk` e o `gh` vão para a peça dos processos ("os
   nossos processos" hoje são OCR, Kraken, servidor de páginas e brasão).
2. **"Windows pelo ctypes" vale em todo arquivo, não só no dono das DLLs.** O pedido diz "dentro de
   `core/nativo_dll.py`". Fiz como capacidade com um dono (`core/windows.py`), que é uma regra num lugar só. Por isso
   ela também acusa fora do dono, onde o `import ctypes` já era acusado: são 13 das 46 chaves. Ela separa sozinha o
   ctypes do Windows (vai para `core/windows.py`) do ctypes das DLLs (vai para `core/nativo_dll.py`). Acusar só dentro
   do `core/nativo_dll.py` daria 33 chaves, mas seria uma regra só para um arquivo.
3. **A catraca não impede a troca de uma linha por outra.** Quem conserta um lugar e, na mesma mudança, põe um lugar
   novo na lista no lugar dele, mantém o tamanho e passa no `<= TETO`. Só a revisão da mudança pega. Com `<=`, também
   não é obrigatório abaixar o teto ao tirar linha (a mensagem pede, mas passa sem). Pôr `==` obrigaria a abaixar e
   fecharia essa folga; não pus porque o pedido diz `<=`.

## Ressalvas

1. O mesmo jeito repetido na mesma função é um lugar só. Um segundo `windll` dentro de uma função que já tem um não é
   lugar novo. Um `windll` numa função nova é.
2. Renomear uma função muda a chave dos lugares dela: a catraca acusa um novo e um que sumiu, e a lista precisa ser
   trocada (é a troca do ponto 3 acima, por motivo bom).
3. Atributo com nome do Windows é acusado venha de onde vier (`x.GetLastError`). Hoje não dá alarme falso no programa.
   Se um dia der, aparece como lugar novo, nunca calado.
4. O motor do Kraken é lido procurando na pasta dele. Se um dia ele importar `core.x`, a trava não segue (no motor o
   `core` não vai junto, e o import quebraria lá).
5. O que a trava não pega continua escrito na docstring do teste.
6. **Três provas da segunda volta, deste mesmo arquivo, mudaram** porque o mapa mudou:
   `test_cada_dono_usa_a_sua_capacidade_e_nao_a_dos_outros` (o Windows agora pode `subprocess`),
   `test_o_mapa_dos_donos_so_usa_capacidades_que_existem` (dois donos do `subprocess`; a capacidade nova) e
   `test_acusa_cada_jeito_de_importar_e_de_usar` (dois achados a mais de "Windows pelo ctypes"). São do arquivo novo
   deste ramo, que ainda não entrou em lugar nenhum; nenhum teste de fora dele mudou.
7. Não disparei a rodada do GitHub (`[skip ci]`; o pedido manda rodar só este arquivo).

## Ideias para a Lista de espera

- Proteger a `LISTA_CONGELADA` e o `TETO` como os arquivos que só a gerente muda (a K17 do porteiro), para a troca de
  uma linha por outra (ponto 3 de "O que não fechou") não passar sem ela ver; e trocar o `<=` por `==`.

---

# Segunda volta — cabeçalho original (23/11/2026)

Implementador. Ramo `atualizador-novo-2026-11-23` (saiu de `obra-2026-10-26` em `c8531595`), worktree
`.claude/worktrees/atualizador-novo`. Pedido da gerente de 23/11/2026.

**Situação: a segunda volta (a última, D-815) está feita e esperando a gerente.** O teste continua em
`tests/test_trava_windows.py`, agora com o desenho dos donos do Fable. A trava acusa **34 lugares** e está marcada
`xfail(strict=True)`. As 14 provas passam, e a pendência do `CDLL` fica parada. A primeira volta, mais abaixo, fica como
histórico.

# Segunda volta (D-815, recado da gerente com a resposta do Fable aos 7 pontos)

## O que mudou no teste

- **A pergunta é outra.** Antes era "este import é permitido?". Agora é "quem é o dono desta capacidade?". O mapa está
  escrito uma vez, em `DONOS`, e as capacidades em `CAPACIDADES`.
  - `core/windows.py` pode `ctypes`, `winreg` e `os.startfile`.
  - `core/nativo_dll.py` pode `ctypes` e é o único que pode carregar DLL (`CDLL`, `cdll`, `PyDLL`, `pydll`).
  - `core/processos.py` pode `subprocess`.
  - "Rodar programa pelo `os`" (`os.system`, `os.popen`, `os.spawn*`, `os.exec*`) não tem dono.
  - O dono é acusado pelas capacidades que não são dele.
- **O que é programa:** o fechamento das importações a partir do `main.py` (`fechamento`). Não é lista nem a
  definição do porteiro. Hoje dá 121 arquivos, e nenhum deixou de ser lido.
  - **Importação dentro de função, de `if` e de `try`:** entra. O motivo é que o PyInstaller põe as quatro no `.exe`. A
    fonte é o PyInstaller 6.21.0 instalado, `PyInstaller/building/build_main.py`, linhas 60-77: `IMPORT_TYPES` e o
    texto "conditional: imported within an if-statement / delayed: imported within a function / optional: imported
    within a try-except-statement".
  - **`__import__("x")` e `importlib.import_module("x")` com o nome escrito por inteiro:** entram. O PyInstaller não os
    segue ("Analysis can detect nothing", https://pyinstaller.org/en/stable/when-things-go-wrong.html), mas o programa
    os carrega quando roda. O nome numa variável não se segue.
  - **Pacotes de cima** (`a/__init__.py` ao importar `a.b`) e **o `x` de `from a import x`** entram. O relativo vira
    absoluto. O que não é do repositório não entra. Ciclo não trava.
- **`CDLL`:** a trava só diz quem pode chamá-lo. O teste de execução ("todo caminho carregado está sob `core/nativo/`")
  está escrito como pendência, `test_pendencia_o_dono_das_dlls_so_carrega_dll_de_core_nativo`.
  - Ele fica parado enquanto `core/nativo_dll.py` não existe.
  - Ele falha no dia em que a peça existir sem a prova escrita.
  - A peça não foi inventada.
- **Marca:** `@pytest.mark.xfail(strict=True, reason="D-830: lista de trabalho do atualizador novo")`, só na trava.

## A nova contagem: 34 lugares

**(a1) Atualizador e testes à distância (10).** É a lista de trabalho do atualizador novo.
- `atualizacao.py`: 114 (`subprocess`), 432, 433, 750, 759 (`ctypes`), 1194, 1279 (`winreg`).
- `core/_testes_a_distancia_windows.py`: 32, 36 (`ctypes`), 34 (`subprocess`).

**(a2) Windows de verdade em outras partes (6).** Nada mudado nelas.
- `core/nucleos.py:44`: `ctypes`. A linha 78 usa o `kernel32` para ler a memória livre.
- `core/ocr_comum.py:209`: `ctypes`. A linha 211 usa `WinDLL kernel32` e o `SetDllDirectoryW`.
- `historico.py:7`: `subprocess`, para o `explorer /select`.
- `historico.py:199` e `:212`: `os.startfile`, para abrir a pasta e para imprimir.
- `ui/brasao_girando.py:223`: `ctypes`. Usa o `OpenProcess` para saber se o programa continua aberto.

**(b) DLL nossa (12).**
- Os `import ctypes`, mesmo os que só pegam os tipos: `core/caixas_scantailor.py:82`, `core/cores_scantailor.py:52`,
  `core/desentortar_scantailor.py:69`, `core/dividir_scantailor.py:45`, `core/endireitar_scantailor.py:62`,
  `core/gravura_scantailor.py:47`, `core/luz_scantailor.py:46`, `core/pontinhos_scantailor.py:63`,
  `core/preto_e_branco_scantailor.py:60` e `core/st_ferramentas.py:43`.
- Os dois `CDLL`: `core/gravura_scantailor.py:169` e `core/st_ferramentas.py:315`.

**(b) Processo nosso (5).**
- `core/ocr_comum.py:39`
- `core/ocr_kraken.py:89`
- `core/ocr_tesseract.py:87`
- `core/paginas_em_outro_processo.py:64`
- `ui/tela_de_carregamento.py:38`

**O próprio dono do Windows (1).** `core/windows.py:91`: `subprocess`. Ver o ponto 1 de "O que não fecha".

Conta: 10 + 6 + 12 + 5 + 1 = 34.

## O que saiu do escopo pela definição nova, e por quê

Saíram 31 lugares da primeira volta. Os arquivos onde eles estão não são importados a partir do `main.py`, então não
vão no `.exe`.
- `avaliar.py`: 3 lugares (26, 31 e 1655), a régua dos filtros. São a Área de Trabalho e o `python -c`.
- `teste_velocidade.py`: 17 lugares, o PowerShell, o registro e o `kernel32`.
- `compilar_detector_gravura.py`, `compilar_st_ferramentas.py`, `empacotar.py`, `empacotar_teste_velocidade.py` e
  `montar_motor_kraken.py`: os scripts de montar.
- `gerar_prints.py` e `teste_completo.py`.
- `conferencia.py` e `publicar_versao_kaique.py`.
- `teste_bateria.py` e `teste_robustez.py`.

Fora do fechamento há 45 arquivos que o porteiro conta como programa. Eles estão na lista `fora` da conferência que
rodei: os scripts da raiz, `motor_kraken/servidor_kraken.py` e três telas que nada importa (`ui/tela_opcoes.py`,
`ui/widgets/folhear_pdf.py`, `ui/widgets/trilha_ferramentas.py`). Nada entrou no fechamento que o porteiro não contasse
como programa.

## O que não fecha no desenho (não ajeitei: implementei ao pé da letra e deixo para decidir)

1. **O dono do Windows precisa rodar programas do Windows** (`schtasks`, PowerShell, `icacls`: `core/windows.py`, linhas
   1285, 1487 e 1662), mas o mapa não lhe dá `subprocess`. Ao pé da letra, ele é acusado (`core/windows.py:91`). Há
   dois caminhos: ele ganha o `subprocess`, e aí são dois donos do `subprocess`; ou ele pede ao `core/processos.py` para
   rodar, e aí "processos" deixa de ser "os nossos processos". O mesmo vale para o `explorer /select` do `historico.py`.
2. **"Rodar programa pelo `os`" não tem dono no desenho.** Ao pé da letra, ficou proibido em todo lugar, até nos três
   donos. Tem prova: `test_rodar_programa_pelo_os_nao_tem_dono`. Hoje ninguém do programa usa.
3. **O dono das DLLs pode o `ctypes` inteiro.** Então ele poderia chamar o Windows (`windll`, `WinDLL`) sem ser
   acusado. O desenho não separa "ctypes para a DLL nossa" de "ctypes para o Windows", e a trava não separa.
4. **O `.exe` não é só o `main.py`.**
   - O motor do Kraken é um programa à parte (`motor_kraken/servidor_kraken.py`, montado por `montar_motor_kraken.py`)
     e vai para o Kaique. Ele fica fora do fechamento. Hoje não usa nenhuma capacidade, mas a trava não o vigia.
   - O `empacotar.py` também põe `--hidden-import` (`OCULTOS`). Hoje todos os módulos nossos dessa lista já estão no
     fechamento. Um módulo que entrasse só ali escaparia.
5. **O `SetDllDirectoryW` do `core/ocr_comum.py:211`** é do Windows pelo desenho, mas é um passo de "abrir o nosso
   processo". Quando o código for mudado, o `core/processos.py` terá de chamar o `core/windows.py` para isso. É
   coerente, mas fica escrito.

## As provas (14 passam, 1 parada, a trava `xfail`)

Rodei `D:\programas\EditorImpressao\.venv\Scripts\python.exe -m pytest tests\test_trava_windows.py -q` em 23/11/2026.
Resultado: **14 passed, 1 skipped, 1 xfailed.**

- `test_fechamento_dentro_acusa_e_fora_nao_acusa`: o mesmo `import ctypes` é acusado em `core/usa.py`, que o
  `main.py` importa, e não é acusado em `solto.py`, que ninguém importa.
- `test_fechamento_segue_funcao_if_try_relativo_from_e_texto`: a importação dentro de função, de `if`, de `try`, a
  relativa, o `from pacote import modulo`, o `import_module("x")` e o `pacote/__init__.py` entram.
- `test_fechamento_aguenta_ciclo_e_ignora_o_que_nao_e_do_repositorio` e
  `test_fechamento_que_nao_le_e_falha_nunca_passou` (arquivo que não abre, código ilegível, falta do `main.py`).
- `test_cada_dono_usa_a_sua_capacidade_e_nao_a_dos_outros`:
  - o Windows com `ctypes`, `winreg` e `startfile` não é acusado, e com `subprocess` e `CDLL` é;
  - as DLLs com `CDLL` não são acusadas, e com `subprocess` são;
  - os processos com `subprocess` não são acusados, e com `ctypes` são.
- `test_ctypes_so_para_os_tipos_tambem_e_acusado_fora_do_dono`: o `.ctypes` do numpy não é acusado à parte.
- `test_acusa_cada_jeito_de_importar_e_de_usar`: 17 achados, cada um com a capacidade certa.
- `test_rodar_programa_pelo_os_nao_tem_dono`, `test_nao_acusa_comentario_docstring_texto_nem_nome_parecido` (inclui
  `platform.system()` e `x.exec()`), `test_cada_modulo_proibido_e_acusado` (4 módulos) e
  `test_o_mapa_dos_donos_so_usa_capacidades_que_existem`.

## Ressalvas da segunda volta

- **A trava não pega:** `multiprocessing`, `asyncio.create_subprocess_*`, `sys.modules[...]`, o nome montado em
  pedaços, `nt`/`posix`, a importação com o nome numa variável, e o que o `.exe` leva sem o `main.py` importar (ponto 4
  acima). Está escrito na docstring do teste.
- **O `xfail(strict=True)` deixa a rodada passar com a trava falhando.** Se algum lugar sair da lista, ela continua
  `xfail`. Só quando zerar ela vira "passou inesperado" e falha, pedindo para tirar a marca. Então lugar novo também não
  deixa a rodada vermelha. Isso é o efeito da marca pedida, não um defeito.
- **Não disparei a rodada do GitHub** (`[skip ci]`; o pedido manda rodar só este arquivo).

# Primeira volta (histórico; o desenho e a lista de lá foram trocados pela segunda volta)

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

- `cdbaec25`: `tests/test_trava_windows.py` e este ONDE-PAREI, com push no ramo `atualizador-novo-2026-11-23`.
