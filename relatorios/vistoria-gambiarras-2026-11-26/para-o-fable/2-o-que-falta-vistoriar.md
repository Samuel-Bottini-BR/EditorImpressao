# Vistoria das gambiarras: o que já foi lido e o que falta (27/11/2026)

Escrito pela gerente, a partir do `ONDE-PAREI.md` da vistoria e da lista dos arquivos do programa no ramo
`obra-2026-10-26` (ponta `65190e78`). As contas de linhas são do `wc`, sem os testes.

## O que já foi vistoriado

**A tela de trabalho** (`ui/tela_conferir.py`, 10.187 linhas, e o que ela chama), em 8 pedaços, em 26/11/2026:
girar (12 achados), dividir (16), desfazer (8), aplicar em (8), como fica (5), marcações (5), contagens e situação da
página (15), o resto da tela (12). **81 achados: 30 graves, 31 médios, 20 leves.** Lista completa em `lista.md`.

Dentro da própria tela de trabalho ficou **sem ler**, de propósito (o agente achou só montagem de botões e desenho,
sem conta, pelas buscas): `_montar` e a barra de baixo (L766-1362), o corpo de `_montar_aba_*` (L1916-3653, fora das
linhas citadas no ONDE-PAREI), `_LugaresDeEncaixe`/`_RotuloDoLivro` (L432-590), a "peça" nos pares (L8700-8800) e o
zoom (L8478-8560, L9006-9088).

Dos outros arquivos, a vistoria leu **só os trechos** que a tela chama (estão listados no ONDE-PAREI). Nenhum outro
arquivo foi lido inteiro.

**Uma suspeita ficou aberta**, de fora da tela: `core/pipeline._guardar_o_conteudo` (L1958-1968) não troca o tamanho
de uma página já medida, e o motivo escrito no comentário parece ter deixado de valer no mesmo commit de 21/10
(`57de8af4`).

**Ressalva da gerente:** os pedaços foram rápidos (3 a 14 minutos cada, ~70 min no total). A profundidade só foi
conferida à mão num achado (MC-01: as linhas batem). Os agentes não rodaram o programa; o que depende de uso está
marcado "pela leitura, não rodei".

## O que falta vistoriar: o resto do programa

A ordem de serviço só pediu a tela de trabalho primeiro; o resto **não foi dividido em pedaços por ninguém**. Abaixo,
uma divisão **sugerida pela gerente** (o Samuel decide), por assunto, na ordem de quanto o Kaique usa:

| nº | pedaço sugerido | arquivos | linhas | o que tem |
|---|---|---|---|---|
| 1 | As peças da tela de trabalho | 27 | 15.041 | painéis, visualizador, seleção à mão, tira de miniaturas, grade "Todas as páginas", tela cheia, comparar, botões de girar, menu, desfazer nesta página |
| 2 | Preparar a página (geometria) | 21 | 13.290 | `core/pipeline.py` (5.323), girar, dividir (automático e à mão), cortar, borda preta, endireitar, desentortar, etapas, ordem do preparo |
| 3 | Filtros e limpeza | 14 | 9.346 | `core/filtros.py` (4.483), Só as letras, camadas, Tirar o fundo, peças do ScanTailor (preto e branco, cores, luz, pontinhos) |
| 4 | Gravuras e marcações | 6 | 3.860 | achar gravura, seleção, zonas presas à folha, editar zonas, rede de segmentação |
| 5 | Automático e avisos | 7 | 7.088 | painel Automático (tela e núcleo), análise, "Para revisar", avisos, página em branco |
| 6 | Abrir, guardar e desfazer | 19 | 13.021 | projetos, modelos (`ConfigFolha`/`ConfigPagina`), histórico de ações, configurações, ler o PDF, páginas em outro processo, tela inicial, janela principal, tarefas |
| 7 | Gerar o PDF e cadernos | 8 | 4.748 | impressão, cadernos, impressora, ordem das páginas, janela de montar para imprimir, tela final |
| 8 | Atualizador, Windows e instalação | 13 | 8.220 | `atualizacao.py`, `core/windows.py` (3.375), fases da atualização, Velopack, testes à distância, `main.py`, assinatura |
| 9 | Achar texto (OCR) | 7 | 2.551 | Kraken, Tesseract, docTR e o servidor do Kraken |
| 10 | Ferramentas do Samuel | 9 | 5.624 | empacotar, publicar a versão, servidor das versões, montar o motor, compilar as peças do ScanTailor |

**Total que falta: 131 arquivos, ~82.800 linhas** (a tela de trabalho tinha 10.187).

**Fora da divisão:** 33 scripts soltos de teste e de régua na raiz (`teste_*.py`, `avaliar*.py`, `conferencia.py`,
`rodada_*.py` etc., ~20.000 linhas) e as regras dos agentes (`regras_dos_agentes/`, 18 arquivos, 5.209 linhas). Não são
o programa do Kaique; a gerente sugere deixar de fora, a menos que o Samuel ou o Fable queiram.

## Observações para quem decide a ordem

- O pedaço 8 (atualizador) já passou por cinco rodadas de "quem tenta quebrar" entre 23 e 25/11. Pode ir por último,
  ou só com o tipo 5 (código morto) e o tipo 4 (peças de proteção).
- Os pedaços 1, 2 e 3 são os que mais aparecem nos achados da tela (a tela chama o núcleo por eles). Muitos achados da
  lista apontam "a outra cópia" para dentro deles, e eles ainda não foram lidos inteiros.
- No ritmo da tela de trabalho (~10.000 linhas em ~70 min de leitura), o resto levaria várias horas de agente. A
  estimativa da gerente da última vez errou para cima; esta também pode errar.
