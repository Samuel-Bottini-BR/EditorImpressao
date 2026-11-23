# Conferência dos apontamentos do relatório para o Fable

23/11/2026. Verificador, só leitura (nenhum código, nenhum outro arquivo da pasta mudou; git só `show`, `log`,
`grep`, `diff`, `ls-tree`, `branch -r --contains`, `worktree list`). Conferido por **máquina**: cada link aberto com
`git show <commit>:<caminho>` e comparado linha a linha com a frase. Eu não escrevi nada do relatório.

## Resumo

- **Links do GitHub:** 183 (o 184º, na linha 889 do relatório, é o modelo `O/<caminho>`, não é link).
  - **183 de 183:** o commit está num ramo do GitHub (`git branch -r --contains`) e o arquivo existe no commit.
  - **177 certos sem ressalva**: a linha mostra o que a frase diz, com folga de até 3 linhas.
  - **6 com ressalva** (lista abaixo). Nenhum aponta arquivo ou commit errado.
- **Commits citados sem link:** 41 conferidos (Girar, filtro, atualizador). Todos existem num ramo do GitHub e as datas
  batem.
- **Trechos de código colados:** os 7 batem com o commit citado (o Girar, o Marcar, e os médios 1 a 5). Os cortes com
  "..." e os comentários acrescentados não mudam o sentido.
- **Números:** a maioria bate. Há 6 errados e 5 imprecisos, listados abaixo.
- **Links para fora** (Velopack 1.2.161, docs.velopack.io, learn.microsoft.com): a forma está certa. Não abri nenhum.

## Links com ressalva

1. **Linha 425 do relatório.** A frase diz "`manager.rs:406`, `stub.rs:39-41`, segundo o escritor (ONDE-PAREI L1363)".
   - O que a fonte mostra: `046c0271:relatorios/atualizador-4/ONDE-PAREI.md`, L1363, é só o título da seção "O que li da
     peça de fora e onde". As duas citações estão em L1376 (`manager.rs:406`) e L1377 (`stub.rs:39-41`).
   - Correção: `#L1376-L1377`.
2. **Linha 408.** "resposta 4 da gerente, não do Samuel ([ONDE-PAREI L1423])".
   - O que a fonte mostra: L1423 é o título "Respostas da gerente (volta 4)". A resposta 4 está em L1428 ("A troca sem
     o script também com a mesma marca").
   - Correção: `#L1428`.
3. **Linha 433.** "baixo 2 do [relatório 3](...relatorio-3.md#L99)".
   - O que a fonte mostra: L99 é o título "Baixos". O baixo 2 (o documento do `Start-Process`) está em L106.
   - Correção: `#L106`.
4. **Linha 443.** "Relatório 1: NÃO ESTÁ PRONTO, 3 médios [...] e 11 baixos ([R1 L8])".
   - O que a fonte mostra: o veredito e os 3 médios batem. Mas a seção "Os baixos" do relatório 1 (L152-L180) numera
     **10** baixos. Quem fala em "11 baixos do relatório 1" é o relatório 2 (L118).
   - Correção: "10 baixos numerados (o relatório 2 conta 11)", ou apontar de onde vem o 11º.
5. **Linha 401.** "o pedido sai 17-20 s depois do clique porque o programa primeiro carrega e lê o Windows"
   (`A:2052-2054`).
   - O que a fonte mostra: o comentário diz "o programa carrega e monta a janela antes"; não fala em ler o Windows.
   - Correção: "porque o programa primeiro carrega e monta a janela".
6. **Linhas 316-317 e 322-323.** Vários números de decisão com um link só.
   - "D-715/D-720 [...] D-734 [L1024]": L1024 é só a D-734. A D-715 está em L1005 e a D-720 em L1010.
   - "D-735/D-741/D-749 [L1031]": L1031 é só a D-741. A D-735 está em L1025 e a D-749 em L1039.
   - Não está errado, mas o leitor que abre o link só vê uma das decisões.

## Números errados

| Frase do relatório | O que a fonte mostra | Comando |
|---|---|---|
| L72: "77 arquivos de `core/`+`ui/` diferentes (+30.060 / -1.956 linhas)" | Só `core/`+`ui/`: **75 arquivos, +29.584 / -1.950**. O 77 / +30.060 / -1.956 sai quando se soma também `modelos.py` e `projetos.py` | `git diff --shortstat 47394b4a 0f58346a -- core ui` (e o mesmo com `modelos.py projetos.py`) |
| L135: "`Projeto` (L537, 58 campos)" | **49 campos** (`ConfigFolha` 18 e `ConfigPagina` 51 batem) | contagem dos campos anotados da classe com `ast`, numa cópia de `git show 0f58346a:modelos.py` |
| L264: "M7, 25 testes `getattr(..., "inserida", ...)`" | **26** em `core/`, `ui/` e `modelos.py` | `git grep -E 'getattr\([^)]*"inserida"' 0f58346a -- core ui modelos.py` |
| L691: "Em 23/11 havia mais de 20 worktrees" | **200 worktrees**, 194 em `.claude/worktrees/` | `git worktree list --porcelain \| grep -c "^worktree "` |
| L660: "Desde 21/11 (D-815), quem confere é um agente novo a cada volta" | A D-815 é de **20/11** (Livro L1105) | `git show 0f58346a:docs/plano/DECISOES.md`, L1105 |
| L917: "relatorios/ (3912)" | **3913** | `git ls-tree -r --name-only 0f58346a -- relatorios \| wc -l` |

## Números imprecisos (a frase dá a entender outra coisa)

1. **L270-272 e L831.** O relatório diz que a família F2 do catálogo voltou "nas seis voltas [...] (19, 9, 7, 6, 3 e 1
   achados)", e que "o passo 0 do atualizador teve 6 rodadas de conferência".
   - O que a fonte mostra: 19, 9, 7, 6, 3 e 1 são **todos os achados** de cada volta do passo 0, de todas as famílias.
     Somam 45 e estão no catálogo, L88, fora do trecho L131-L163 que o relatório aponta. A F2 sozinha tem 19 erros nos
     passos 0 e 1 (L158).
   - O passo 0 é "o porteiro" do plano da parte do Windows (catálogo L79), não o atualizador.
   - Correção: "o passo 0 (o porteiro) teve seis voltas de quem tentou quebrar, com 19, 9, 7, 6, 3 e 1 achados
     (catálogo L88); a F2 voltou nas seis (L158)".
2. **L541.** "Isso já está anotado: baixo 11 do relatório 1."
   - O que a fonte mostra: o relatório 1 não tem baixo 11. A nota sobre o pedido antigo, que ainda lê o "Não" como
     "Sim", está como "Lembrete" na seção "Pedidos específicos da gerente", L119-L121 (`046c0271`).
   - Correção: "anotado no relatório 1, L119-L121".
3. **L226-227.** "O comentário do Filtro, logo abaixo, diz 'nunca apaga exceção'."
   - O que a fonte mostra: o comentário não está logo abaixo do `_marcacao_em_todas` (L3311). Ele está em
     `_filtro_em_todas`, em `bc766007` L9006 (hoje L9188), umas 5.700 linhas depois.
   - Correção: tirar "logo abaixo" e apontar L9006.
4. **L246.** "`claro_no_escuro` continua só em `CAMPOS_DA_PAGINA`."
   - O que a fonte mostra: ele também está em `MARCAS_DA_PAGINA` (`ui/tela_conferir.py`, `0f58346a`, L10161), que é
     uma das seis listas que o próprio relatório cita. O que é verdade: ele não está em `_campos_do_aplicar_em`
     (L9133-L9163).
5. **L711 e L723-724.** "barreira automática desde 19/11 (D-791)"; "Em 23/11 ela tem 164 lugares".
   - A data: a D-791 é de 18/11 (Livro L1081). O `porteiro.py` nasceu em 18/11 às 22h48 (`8967cc10`). A lista foi
     confirmada e o porteiro ligado no GitHub em 19/11 (D-801). "Desde 19/11" vale para "ligado".
   - Os 164 lugares (52, 50, 33 e 12) batem no `aa1963b7`, o ramo do atualizador. Na versão de teste (`0f58346a`) a
     lista tem 175. Vale dizer de qual ramo é o número.

## Números conferidos que batem (com o comando)

- **Ramos:**
  - 342 commits do `fase-1` depois da separação e 1206 a mais na versão de teste: `git rev-list --count` a partir do
    `git merge-base`.
  - O código do `fase-1` parou em 23/10 (`d746c8df`): `git log -1 47394b4a -- core ui`.
- **`ui/tela_conferir.py`:** 10.187 linhas hoje e 10.041 no `bc766007` (`git show ... | wc -l`).
- **Testes:** 258 arquivos `test_*.py`, 64 `test_decisoes*.py`, 3.641 `def test_`, 19 `teste_*.py` na raiz, 269
  arquivos em `tests/` (`git ls-tree`, `git grep`). O total de **4.668 casos coletados não conferi**: precisaria rodar
  o pytest.
- **Livro de decisões:**
  - 617.985 bytes, 841 linhas de decisão, 804 números únicos, de D-001 a D-829.
  - 8 com "falta o teste" (D-589, D-638, D-640, D-645, D-646, D-663, D-699, D-758).
  - 40 consertos esperando o olho do Samuel (L651).
  - A contagem por situação bate com diferença de 1 ou 2, conforme se classifica a situação mista. A minha: 347
    construídas, 174 não construídas, 46 pela metade, 54 prontas para conferir, 23 a conferir, 28 testadas, 38
    substituídas e 8 descartadas. Não é erro.
- **Plano no `fase-1`:**
  - 8 itens `[x]`, 2 `[~]` e 29 abertos. O 1.1, o 1.2 e o 1.3 foram aprovados em 02/10.
  - Lista de bugs: 273 linhas de dados e 22 caixinhas, 21 abertas.
  - `memoria/bugs.md`: 107 abertos, 58 a conferir, 43 fechados.
- **Revisão de 10/11:**
  - 348 linhas.
  - 17 remendos: 4 altos, 9 médios, 4 baixos.
  - Leu o `bc766007`.
  - A prova do A4 está em L334-L348.
- **Modelo de dados:** `ConfigFolha` tem 18 campos e `ConfigPagina` 51.
- **Atualizador:**
  - `atualizacao.py`: 935 linhas em `16c838a7`, 1681 em `4a775ba8`, 1892 depois da volta 2 (`6efa58d7`), 1942 depois
    da volta 3 (`f15863b8`) e 2314 em `aa1963b7`.
  - `core/windows.py`: 2813 linhas. `core/testes_a_distancia.py`: 877.
  - Os dois arquivos de teste: 915 + 940 = 1855 linhas.
  - `b756ddc2`: 4 + 15 linhas nos dois arquivos de código.
  - `core/_testes_a_distancia_windows.py`: `git diff b74a94e2 aa1963b7` vazio.
  - `plano_de_ligar` tem 9 passos.
  - Os valores: 30 tentativas, 30 s, 10 s, 60 s, 900 s, 120 s, 4 s e 5 min.
  - O relatório 3: 55 testes e 5 médios.
  - A revisão do atualizador de 18/11 achou 13 defeitos novos; a dos testes à distância, 4 causas.
- **Porteiro:** `porteiro.py` tem 1048 linhas; há 25 conferências, de K01 a K25 (`Conferencia("K..` em
  `regras_dos_agentes/`); `New-Item` não está na lista da K01; `.git/hooks/pre-commit` não existe e `core.hooksPath`
  está vazio.
- **Tamanhos dos documentos:**
  - `CLAUDE.md`: 71.186 bytes no `fase-1`.
  - Os agentes: de 10,6 a 14,2 KB (4 arquivos).
  - `PLANO-DEFINITIVO.md`: 395 KB. O histórico: 784 KB. `memoria/INDICE.md`: 12 KB.
  - `docs/plano/central/conferencias/`: 18 arquivos no `fase-1`.
  - `relatorio.gravar` está em L346 do `relatorio.py`.
- **Anexo:**
  - Arquivos por pasta: `core/` 67, `ui/` 49, `terceiros/` 268, `memoria/` 209, `docs/plano/` 69, `regras_dos_agentes/`
    18, `gabarito/` 5.
  - `versao.py` diz "1.1.0".
  - `empacotar.py`: 2036 linhas, e as linhas L64, L68-80, L228-268, L859, L907, L1192, L1530 e L1971 batem.
  - O workflow: Python 3.14.3 em L98, 5 partes, `windows-latest`.
  - As versões do `requirements.txt` e do `.venv` (`*.dist-info`) batem. Kraken 7.1.1 e torch 2.14.0 batem.
  - Os caminhos dos modelos: `detectar_regioes` L158, `rede_selecao` L29-31, `ocr_doctr` L100.

## Afirmações sem apontamento (parecem fato, sem link nem comando)

- L164-167: os 4.668 casos coletados e "rodado da raiz, para em 2 erros de leitura". É o resultado de um comando que eu
  não rodei.
- L729: "Porteiro: nada novo (5000 arquivos lidos; a lista deixa 164 lugares)". É a saída de um comando, sem registro
  guardado.
- L700: "Leva cerca de 2 h" (a rodada inteira no GitHub). Não aponta nenhuma rodada.
- L765: "o quadro dos trabalhos não é atualizado desde 18/11".
- L709 e L810: "a gerente tinha esquecido" e "Em 23/11 disse ao Samuel que não havia barreira automática". Vem do
  chat, sem registro.
- L800: "A volta 4 foi escrita por um agente que leu a regra 12".
- L422-424 e L429: "lido por mim: sim, hoje" para o código do Velopack e para a página da Microsoft. Não dá para
  conferir pelo repositório.
- L963: o notebook do Kaique "i5-1235U, sem placa de vídeo".
- L437: "7 defeitos no Windows de verdade" na etapa 5. A fonte é o CLAUDE.md §11.12, sem link.
- L388-390: os "sete processos em duas contas". Está marcado como dedução, então está certo assim; só lembro que não
  tem prova.
- L113: "dois processos desenham as páginas do PDF". O arquivo existe; o "dois" não conferi.

Fim. Nada foi aprovado aqui. Só o Samuel aprova.
