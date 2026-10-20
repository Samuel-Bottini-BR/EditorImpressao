# Onde parei — acerto do Pesel 21 (implementador, 20/10/2026)

**PRONTO PARA CONFERIR (entregue a gerente em 20/10).** Pedido da gerente: o Pesel 21 tem de sair como no `fase-1` (folha inteira, 157 x 241 mm), sem
perder as cinco melhorias. O Samuel marcou "Melhorar" em 13/10 ("Ele chega a quase cortar as letras.").

Passos:
1. [x] `origin/fase-1` (b8e9af7) juntado ao ramo, sem conflito (`3e1cc3a`).
2. [x] Causa: a pergunta "ha o que recortar?" (`_sem_conteudo_para_recortar`) era feita na pagina girada; o branco
   da cunha mudava a mediana do cartao (102 -> 125) e o Pesel 21 deixava de ser "sem conteudo". No `fase-1` o
   degrau branco da cunha escondia isso (segurava o corte na folha inteira); o conserto de 13/10 tirou o degrau.
   Diagnostico: so a conta da "tinta falsa" muda o Pesel 21 (desligando-a, sai inteiro).
3. [x] Conserto: `detectar_bordas(..., como_veio=)` - a pergunta e feita na pagina antes do giro (a mesma resposta
   da ordem antiga). `core/pipeline.py`: so a chamada. Tirar so a cunha da conta nao bastava (testado).
4. [x] Teste de reversao: `test_cartao_escuro_sai_inteiro_no_livro_novo` (3 angulos, roda no GitHub) e
   `test_pesel_21_sai_como_no_fase_1` (so no PC). Falharam no codigo antigo: `pesel21/reversao-no-codigo-antigo.txt`.
   `tests/test_ordem_do_preparo.py` inteiro: 56 passaram (os 6 da borda preta inclusive).
5. [x] Medida das 89 paginas (`MEDIR_CONFIGS=C`, `MEDIR_SAIDA=dados-pesel21.json`, `MEDIR_SUFIXO=__pesel21`;
   `scripts/comparar_pesel21.py`): contra o d97b937 so o Pesel 21 muda; contra o fase-1, as 9 de 13/10.
6. [x] Projeto antigo 40 de 40 (`projeto-antigo.json`).
7. [x] Antes/depois das 10 (`scripts/montar_pesel21.py`), todas abertas. Relatorio:
   `relatorios/conferir/conserto-corte-g6-pesel21-2026-10-20/pesel21.md`.
8. [x] Suite no GitHub: rodada 39396681554, success: 114 arquivos, 2061 passaram, 0 falharam, 0 erros, 73 pulados (o teste do Pesel 21 de verdade pula la, como previsto; os 3 do cartao de mentira passam); botoes e prints da janela real: success.
9. [x] Filtro de velocidade do GitHub, SO INDICATIVO (o filtro ainda esta sendo montado por outro agente; a gerente mandou nao esperar): rodada 39396712441, fase-1 (b8e9af7) x este ramo (90c9d61), 3 rodadas alternadas: veredito "igual" nas quatro medidas (abrir +1,7%, trocar de pagina -3,7%, Magico pro -4,4%, Preto e branco -1,4%; todas dentro do vai-e-vem). A medida que vale fica para o filtro pronto / o PC no fim da fase.
10. [x] Entregue a gerente (20/10).

---

# Onde parei — conserto do corte do G6 (implementador, 13/10/2026)

**PRONTO PARA CONFERIR.** Ramo `conserto-corte-g6-2026-10-13` (worktree `.claude/worktrees/conserto-corte-g6`,
saído do `fase-1` em `b5b12da`). **Não juntado ao `fase-1`.**

Relatório para ler: `relatorios/conferir/conserto-corte-g6-2026-10-13/conserto-corte-g6.html` (e `.pdf`, `.md`),
com as imagens em `img/tres-*.jpg` (ordem antiga, ordem nova de hoje, ordem nova consertada). As imagens, o
`.html` e o `.pdf` ficam só no disco (o git ignora `relatorios/conferir/**` fora o `.md`); refazem-se com
`scripts/montar.py` e `scripts/relatorio_final.py`.

## O defeito

No livro novo (endireitar antes de cortar, G6) a página é girada inteira e o giro pinta de branco as cunhas das
beiradas. Esse branco escondia a borda preta do scanner da busca do corte: sobrava faixa preta larga em página
torta com borda preta (Matemática 32, Cursus 3, Antiphon 88 e 260, Camões 104). Relatório do verificador: ramo
`verif-corte-g6-2026-10-13`, `relatorios/conferir/corte-g6-2026-10-13/`.

## O que mudou no código

- `core/recortar.py`
  - linhas 36 a 38: importa `ANGULO_MINIMO` de `core/endireitar`;
  - linhas 235 a 471: bloco novo "A cunha do giro" (comentário, `COBERTURA_DE_IMAGEM`, `_cunha_do_giro`,
    `_preencher_a_cunha`, `_tinta_falsa_da_cunha`, `PECA_COLADA_GRANDE`,
    `_sem_as_pecas_grandes_coladas_na_cunha`, `_apagar_bordas_solidas_fora_da_cunha`);
  - `detectar_bordas` (linha 474): parâmetro novo `girada` e o parágrafo dele na docstring; o uso (linhas 535
    a 553 e 563 a 569) e as peças (linhas 603 a 607). Sem `girada`, a conta é a de sempre.
- `core/pipeline.py`: **só a chamada**, em `_geometria_endireitando_antes`: a linha 761 de antes virou as linhas
  761 a 765 (4 de comentário e `detectar_bordas(reta, dpi=dpi, girada=angulo if girar else None)`). Nada mais
  no arquivo. Para juntar com o ramo `fase2-para-revisar`: é a linha logo depois de
  `reta = rotacionar(em_cinza(), angulo) if girar else em_cinza()`.
- `tests/test_ordem_do_preparo.py`: `_corte_na_reta` passa a dizer o giro; testes novos no fim (página torta com
  borda preta na ordem nova, 6 casos; página sem fundo escuro não muda, 3 casos).
- Não mexi em `ui/`, `core/analise.py` nem `modelos.py`.

## Números (programa de verdade, 89 páginas, 300 DPI, sem filtro)

Faixa escura na beirada:

| Página | ordem antiga | ordem nova de hoje | ordem nova consertada |
|---|---|---|---|
| Matemática 32 | 18,4% | 31,5% | **16,8%** |
| Cursus 3 | 0,5% | 7,5% | **1,0%** |
| Antiphon 260 | 3,2% | 7,6% | **3,4%** |
| Antiphon 88 | 8,5% | 12,6% | **7,2%** |
| Camões 104 | 0,5% | 2,7% | **0,9%** |

- Ordem antiga (preparos A e B): idêntica ponto por ponto (md5) nas 89.
- Ordem nova: 79 de 89 idênticas ponto por ponto às de hoje (as 46 que não giram, as 14 do gabarito do G6 e 7
  das 8 que tinham melhorado). Mudam 10: as cinco, Pesel 21 (47,3% → 35,4%; 157 × 241 → 145 × 206 mm, **para
  olhar**), Egenloff 3 (0,5 mm a menos embaixo, uma peça do rodapé da biblioteca de fora), Camões 66, Antiphonal
  252 e Rariora 155 (1 mm ou menos). Pela conta do verificador, nenhuma piora contra hoje.
- Custo: mediana de 18 ms a mais por página que gira (`custo.json`); página que não gira não paga.
- Testes: os 39 arquivos de `tests/` que usam a pipeline ou o corte, um por vez, todos passam
  (`test_ordem_do_preparo.py`: 52 passam). O teste novo falha sem o conserto (`scripts/teste_sem_o_conserto.py`).

## Arquivos desta pasta

- `dados-verificador.json`: a medida do verificador (cópia). `dados-antes.json`: a minha medida de antes (igual
  à dele em 89 de 89), com md5. `dados-depois.json`: a medida de depois (código final menos a troca de ordem de
  uma conta, conferida em `dados-depois-confere.json`). `dados-depois-sem-a-regra-das-pecas.json`: a primeira
  medida de depois (Antiphon 260 ainda em 5,3%).
- `comparacao.json`: as três colunas, página por página. `custo.json`. `projeto-antigo.json`.
- `experiencia.json` (cópias JPEG) e `experiencia-pdf.json` (páginas do PDF): as variantes medidas.
- `scripts/`: `medir.py` e `projeto_antigo.py` (cópias dos do verificador, só os caminhos mudaram),
  `comparar.py`, `montar.py`, `relatorio_final.py`, `custo.py`, `experiencia.py`, `comparar_exp.py`, `olhar.py`,
  `teste_sem_o_conserto.py`.

## Para rodar de novo

```
cd D:\programas\EditorImpressao\.claude\worktrees\conserto-corte-g6
$env:TEMP="$PWD\_tmp"; $env:TMP="$PWD\_tmp"
$py = "D:\programas\EditorImpressao\.venv\Scripts\python.exe"
$s = "relatorios\conserto-corte-g6\scripts"
$env:MEDIR_SAIDA="dados-depois.json"; $env:MEDIR_SUFIXO="__depois"
& $py $s\medir.py        # pula o que ja esta no json
& $py $s\comparar.py
& $py $s\montar.py
& $py $s\relatorio_final.py
```

As páginas prontas a 300 DPI ficam em `_tmp\finais\` (fora do git). A experiência e o `custo.py` leem as cópias
JPEG da worktree do verificador (`.claude/worktrees/verif-corte-g6/_tmp/finais`).

## O que falta (não é meu)

- O verificador abrir as imagens (`img/tres-*.jpg`), principalmente Pesel 21, Cursus 3, Egenloff 3 e as cinco.
- O teste de velocidade (`teste_velocidade.py`), que não rodei.
- A gerente juntar ao `fase-1` depois de conferido.

## Fora desta tarefa (só relato)

- Escola 197 (números da margem cortados): não mexi; continua igual a hoje.
- `_apagar_riscas_de_dobra` apagando linhas de texto da máscara no Cursus 3: continua (o conserto soma ao apagar
  de hoje, não o troca).
