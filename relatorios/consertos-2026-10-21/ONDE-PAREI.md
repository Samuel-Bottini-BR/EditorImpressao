# Consertos de 21/10/2026: onde parei

**Quem:** agente implementador · **Ramo:** `consertos-2026-10-21` (saiu do `fase-1` `31a9253`) · **Pedido:** gerente, 21/10.

## Em uma frase

Os dois bugs da Lista de bugs estão consertados, cada um com teste de reversão que falha sem o conserto.

## 1. Instalador sem a `st_ferramentas.dll` (Lista de bugs, 20/10) — `81315e7`

- `empacotar.py`: `nativos_do_programa` leva as duas DLLs do ScanTailor e o `.txt` de cada uma
  (`st_gravura` e `st_ferramentas`); `core.st_ferramentas` entrou nos `--hidden-import`; a
  mensagem de DLL faltando cita os dois compiladores.
- `instalador.iss`: a mesma trava `#error` da `st_gravura` para a `st_ferramentas.dll` e o `.txt`.
- Teste de reversão `tests/test_empacotar.py::test_regressao_o_pacote_leva_as_duas_dlls_do_scantailor`:
  falhou no código antigo ("st_ferramentas.dll não vai para o pacote"); passa no novo. Dois testes
  antigos acertados para as quatro peças (registro do Inno com as duas DLLs).
- `tests/test_empacotar.py`: 41 passaram.
- **Não feito:** gerar o instalador de verdade (Inno Setup) e conferir a pasta empacotada.

## 2. Teste que depende da ordem (Lista de bugs, 20/10) — `0e763f1`, `6411221`

- Causa: o registro de atalhos (`atalhos.py`) é global e é preenchido uma vez, ao importar as telas
  (`ui/tela_conferir.py` registra "Espelhado" e "Proporção travada" na importação). O
  `tests/test_atalhos.py` esvaziava o registro e não o devolvia; quando a tela já tinha sido
  importada na coleta (por `tests/test_endireitar_na_tela.py`, por exemplo), o
  `test_paineis_na_tela.py::test_espelhado_e_proporcao_travada_sao_caixinhas_e_as_teclas_valem` via
  "Espelhado   (tecla )".
- Reproduzido: `pytest tests/test_atalhos.py tests/test_endireitar_na_tela.py
  tests/test_paineis_na_tela.py::test_espelhado...` falhava.
- Conserto: `tests/conftest.py` (`_atalhos_isolados`) devolve, no fim de cada teste, toda tecla que
  já existia (as que nascem no teste, de tela importada pela primeira vez, ficam);
  `tests/test_atalhos.py` devolve o registro exato (as teclas dele são de mentira).
- Primeira versão (`0e763f1`) errada: devolvia a cópia tirada antes de a tela ser importada e apagava
  os atalhos da tela; o arquivo dos painéis falhava sozinho. Corrigida em `6411221`.
- Teste de reversão `tests/test_atalhos.py::test_regressao_quem_vem_depois_ve_o_registro_de_antes` (desde 21/10 em
  `tests/test_reversao_atalhos_ordem.py`, arquivo só dele, a pedido do verificador):
  roda, num processo à parte, a ordem que falhava; falha sem o conserto ("tecla )"), passa com ele.
- Seis arquivos de tela/atalhos em sequência (atalhos, menu, endireitar, girar, painéis, trilha):
  103 passaram.

## GitHub

- [x] Suíte no Windows do GitHub, rodada 39559866204 (código `e414ba1`): 115 arquivos, 2074 passaram,
      0 falharam, 73 pulados; botões e prints da janela real: passou.

## 4. Horas p. 11 em Mágico pro nem sempre dá a mesma imagem (Lista de bugs, 20/10)

- Causa achada: com pouca memória, dois caminhos trocavam a conta em silêncio: (1) o modelo de layout
  (`doclayout.onnx`) que falhava na carga ficava fora a sessão inteira; (2) o detector de gravura, ao
  responder "faltou memória", caía no detector antigo naquela página.
- Prova na página de verdade (`scripts/horas11_soma.py`): normal, duas vezes em processos separados,
  `b85e5b05…` (a soma das 4 repetições da prova "sai igual"); com a falta de memória da gravura simulada,
  `183af29c…` (outra imagem).
- Conserto: a carga que falhou é tentada de novo na página seguinte (arquivo/biblioteca ausentes ficam de
  vez); a falta de memória da gravura é tentada de novo depois de `gc.collect()`.
- Teste de reversão `tests/test_mesma_imagem_com_pouca_memoria.py` (2 falham antes, passam depois).
- Ressalva: não reproduzi a falta de memória de verdade (só simulada); se faltar memória nas duas
  tentativas, a página ainda cai no detector antigo (com o aviso de sempre na tela e no erros.log).
