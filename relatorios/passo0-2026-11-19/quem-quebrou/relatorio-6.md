# Passo 0 do plano da parte do Windows: sexta conferência de quem tentou quebrar (19/11/2026)

Esta é a sexta volta do mesmo verificador, que não escreveu o passo 0. Conferi os consertos de S1, S2 e S3 pelo mesmo
caminho e pelos vizinhos, e respondi se o caso `import docs.segredo` é grave hoje. Não mexi no código entregue.

## Pedido

- Papel: quebrador
- Commit de partida: 89f80080
- Ramo: passo0-porteiro-2026-11-19

## Arquivos que vou mexer

- `relatorios/passo0-2026-11-19/quem-quebrou/`

## Veredito

"PRONTO PARA CONFERIR"

Nos termos da D-798: quem escreve é quem tentou quebrar, que não construiu nada deste passo. Todos os achados das seis
voltas têm destino resolvido, e este passo não tem prova à vista, porque nada nele mexe no Windows (plano-v3, passo 0;
D-785). Isto não é aprovação: só o Samuel aprova.

Nesta volta:
- S1, S2 e S3 estão consertados no commit `b5927774`, com teste de reversão provado por mim.
- O caso `import docs.segredo` **não é grave hoje**. Fica registrado como ressalva e como ideia na Lista de espera (T1).

## O que li

- O `relatorios/passo0-2026-11-19/ONDE-PAREI.md` na ponta `89f80080`: "Como ficou cada achado da quinta volta", as
  ressalvas e as ideias.
- O código mudado de `65843bb3` a `b5927774`: `porteiro.py` (`NAO_E_PROGRAMA` sem `historico`, `FONTE_PYTHON`,
  `COMPILADO_PYTHON`, `pastas_de_fora_com_nome_de_modulo`), `porteiro_mudancas.py`, `formulario.py`, `protecao.py` e
  os testes novos.
- A rodada 44487102520: "success".

## O que conferi nas falhas, nas peças de fora e nos caminhos

- **S1, o jeito novo se sustenta.** `historico` saiu da lista das pastas que não são programa. O porteiro passa a ler
  `historico/`, que hoje não tem nenhum `.py`, então a lista continua com 176 lugares, o que conferi. E qualquer pasta
  da lista com o nome de um arquivo de código da raiz vira K00, que nunca entra na lista.
  - Mesmo caminho: `historico/__init__.py` com `schtasks` agora é acusado (K01).
  - Vizinhos: um `docs.py` na raiz com `docs/x.py` dá K00 em `docs`; um `tests.pyw` na raiz dá K00 em `tests`.
  - No repositório de hoje, nenhuma colisão.
  - Esse jeito é melhor que acusar `__init__.py` nas pastas da lista: o `tests/__init__.py` existe de propósito e
    precisaria de exceção.
- **S2, consertado.** `core/x.pyw` com `schtasks` é acusado. `FONTE_PYTHON` (`.py` e `.pyw`) é a lista única que as
  conferências consultam.
- **S3, consertado.** `core/x.cp314-win_amd64.pyd` dá K00. A `.dll` do ScanTailor fica de fora, e é certo: o Python
  não a importa como módulo, e o ctypes que a carrega já é acusado pela busca do Windows.
- **Teste de reversão provado por mim.** Com o `regras_dos_agentes/` de `65843bb3`, os três testes falham:
  `test_s1_a_pasta_com_nome_de_modulo_e_lida_e_a_colisao_e_acusada`, `test_s2_o_pyw_e_lido_como_codigo` e
  `test_s3_a_extensao_compilada_pyd_e_acusada`. No código novo, passam.
- **O caso `import docs.segredo`, e o vizinho do arquivo `.zip` posto no caminho de busca do Python.** Provei que
  passa: `main.py` com `import docs.segredo` e `docs/segredo.py` com `schtasks` não dão achado. O mesmo vale para
  `sys.path.insert(0, "core/extra.zip")` seguido de um `import`.
  - Não é grave hoje. Nenhum arquivo do programa importa das pastas de fora. Só três scripts da raiz que não vão para o
    Kaique importam `tests.ajudante_do_automatico`, e esse arquivo não conversa com o Windows (conferido com a busca).
    Os `sys.path.insert` de hoje só põem a raiz do projeto.
  - Para usar esse caminho, é preciso escrever de propósito uma linha nova de import ou de caminho no programa, e essa
    linha aparece no diff para quem tenta quebrar e para a gerente.
- **Nada mudou fora do combinado.** Desde `746dbda6`, só arquivos novos em `regras_dos_agentes/`, `ganchos/`,
  `relatorios/passo0-2026-11-19/`, `tests/test_conferencias_*` e a lista.

## Caminhos que o outro não listou

- O vizinho do arquivo `.zip` no caminho de busca do Python, que é da mesma família do `import docs.segredo`. Fica
  junto com ele (T1).

## Falhas não pensadas e resultado não conferido

- Nenhuma nova. O formulário ficar "não conferido" até a gerente ligar a lista é o combinado, fora da conta.

## As regras que conferi

- **CLAUDE.md §11.12:**
  - pontos 1 a 4: cumpridos;
  - ponto 3, a lista do que pode falhar: as falhas que sobram estão escritas nas ressalvas.
- **CLAUDE.md §4.7:** teste de reversão provado.
- **CLAUDE.md §11.7**, só o que ele mandou: acusar import de pasta de fora seria uma conferência nova, além das 24 da
  proposta. Por isso o lugar certo é a Lista de espera, e não um conserto agora.
- **Decisões tocadas:** D-791, D-792, D-796, D-798, D-800, D-605 e D-784, todas cumpridas.

## Achados

1. **T1, baixo: o programa pode importar código de uma pasta de fora (`import docs.segredo`) ou de um `.zip` posto no
   caminho de busca, e o porteiro não lê esse código** (`regras_dos_agentes/porteiro.py:130`, `NAO_E_PROGRAMA`).
   - Provado com um exemplo; hoje não acontece em nenhum lugar do programa.
   - Destino: não é defeito deste passo, e já está registrado. Está escrito nas ressalvas do ONDE-PAREI ("Importar
     direto uma pasta de fora") e como ideia para a Lista de espera, porque seria uma conferência nova (§11.7).
   - Peço à gerente que o "`.zip` no caminho de busca" entre na mesma ideia, e que quem tentar quebrar os próximos
     passos olhe no diff toda linha nova de import de pasta de fora e de mudança no caminho de busca.

Os achados das voltas anteriores e o destino de cada um:
- **1 a 19** (relatório 1): consertados nos commits das voltas, menos o 11, que é o combinado do plano, e o 17, que
  virou pergunta à gerente.
- **N1 a N9, R1 a R7 e Q1 a Q7**: consertados (o Q3 também com o aviso no pacote). O Q5 é o combinado, e o Q7 foi
  aceito pela gerente.
- **S1 a S3**: consertados em `b5927774`.

## Para a gerente: o que ficou fora do projeto

- Na cópia temporária (`C:\Users\fotog\AppData\Local\Temp\claude\b9ca076ad002e817\848d7b72-406b-4bfe-aabf-f5b3005d7b22\scratchpad\quebrar\copia`)
  ficou mais o ramo de prova `prova6`.
- Nada foi apagado. A lista inteira do que deixei na pasta temporária está nos relatórios 1 a 5. A gerente pergunta
  ao Samuel se pode apagar.
