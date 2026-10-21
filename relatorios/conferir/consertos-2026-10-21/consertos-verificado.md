# Consertos de 21/10 (instalador e teste que depende da ordem) - conferência do verificador (21/10/2026)

Ramo `consertos-2026-10-21`, código `fb9de49`, contra o `fase-1` `31a9253`. Não mudei código; não marco nada como aprovado. (O ramo já tem um commit a mais, `c97661c`, da Gladstone 18: não conferido aqui.)

## Veredito

**PRONTO PARA CONFERIR.** Os dois consertos fazem o que dizem e os dois testes de reversão falham sem o conserto. Uma ressalva sobre o segundo teste (abaixo). Isto é só teste de máquina, sem janela: não precisa da conferência em fotos do Samuel.

## 1. Instalador sem a `st_ferramentas.dll`

| O que | Resultado |
|---|---|
| `tests/test_empacotar.py` no `fb9de49` | 41 passaram |
| O mesmo arquivo no `31a9253` (reversão) | 3 falham: `test_regressao_o_pacote_leva_as_duas_dlls_do_scantailor` ("st_ferramentas.dll não vai para o pacote") e os dois testes antigos acertados |
| `empacotar.nativos_do_programa()` chamado de verdade | devolve as 4 peças: `st_gravura.dll` e `.txt`, `st_ferramentas.dll` e `.txt`, em `core/nativo` |
| `instalador.iss` | trava `#error` para a `st_ferramentas.dll` e o `.txt` (linhas 56 a 60) |

Não gerei o instalador de verdade (Inno Setup), e o implementador também não.

## 2. Teste que depende da ordem (atalhos)

| O que | Resultado |
|---|---|
| A ordem que falhava (`test_atalhos.py`, `test_endireitar_na_tela.py`, o teste do Espelhado), no `31a9253` | falha: "Espelhado   (tecla )" |
| A mesma ordem no `fb9de49` | 22 passaram |
| Reversão: só o teste novo, sem nenhuma parte do conserto, no `31a9253` | falha: "assert 'tecla M' in 'Espelhado   (tecla )'" |
| Seis arquivos de tela e atalhos em sequência, no `fb9de49` | 115 passaram |
| `test_paineis_na_tela.py` sozinho, no `fb9de49` (o que a primeira versão quebrava) | 22 passaram |

**Ressalva:** o teste de reversão fica no mesmo arquivo que leva metade do conserto (`registro_limpo` em `tests/test_atalhos.py`). Copiado inteiro para o código antigo, ele **passa**: 16 passaram, porque o arquivo novo já devolve o registro. Ele só falha quando vai sozinho, sem o resto do arquivo novo. É assim que conferi.
