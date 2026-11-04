# Ajustes do Dividir e da janela do Automático (03/11/2026)

**Os seis achados do verificador clicando de 03/11 estão resolvidos ou respondidos, sem mudar o que já estava
escolhido.** Cinco foram consertados (motor na folha juntada, aviso do "juntar todas", setas depois da lista, tira
depois do Ctrl+Z, etapa 6 cortada). O sexto ("7 com dúvida") não é defeito: são as páginas em branco do livro, e o
"dividir esta" folha a folha dá as mesmas 7. PRONTO PARA CONFERIR (quem confere é o verificador e o Samuel).

Ramo `dividir-ajustes-2026-11-03` (saiu de `75ed04af`). Testes: de máquina. Prints: na janela de verdade do Windows,
posta fora da tela, no Gradus Primus copiado para uma pasta de dados só desta tarefa
(`piloto.py`, anotações em `anotacoes.txt`).

## Decisões que esta tarefa precisava cumprir — como cumpri cada uma

| Decisão | Como cumpri | Prova |
|---|---|---|
| **D-606** "Ele deve fazer a conta novamente com o novo motor" | Na folha juntada, trocar o motor lê a folha pelo motor novo e a linha vai para onde ele acha; o Ctrl+Z devolve motor e linha | Gradus folha 5: linha de antes 0,44 → motor "o do Editor" → 0,5033 (p02, p03). `tests/test_decisoes_dividir.py::test_reversao_d606_*` e `test_d606_depois_do_juntar_todas_*` |
| **D-607** "só temos que mudar o aviso, avisar que as páginas foram juntadas e que vão ser separadas se o processar continuar." | Só o texto muda. Título, explicação de baixo, botões, contagem e o que cada botão faz ficam iguais | p07 (Gradus, 70 juntadas). `tests/test_decisoes_automatico.py::test_*d607*` (4) |
| **D-605** o novo não estraga o escolhido | Lista "O que já está escolhido e testado" no ONDE-PAREI antes de mexer; nenhum teste antigo mudou; todos passam no PC (um por um) e no GitHub | ver "Testes" |
| **D-602** linha azul, "dividir esta", "dividir todas", lista nunca trava | Nada mudou nisso; `tests/test_decisoes_dividir_linha.py` passa sem mudança (13) | PC e GitHub |
| **D-498** "não dividir esta" devolve a linha de antes | Continua enquanto o motor não é trocado (p02: 0,44 depois de juntar) | `test_d602_folha_juntada_mostra_a_linha_de_antes` e o novo teste D-606 |
| **D-090** "usar em todas" copia a linha desta folha · **D-601** arrastar em "Duas lado a lado" | Não mexidos | `test_d602_usar_em_todas_*`, `test_decisoes_dividir_metade.py` |
| **D-004** pular as mexidas · **D-590** caixinha desmarcada fica | Contagem, botões e o pular iguais; caixinha não mexida | `test_d004_*`, `test_decisoes_juntar_todas.py`, `test_dividir_desmarcada_caixinha.py` |

## Item por item

1. **D-606, motor na folha juntada.** Antes a linha ficava parada nos dois motores. Agora a troca do motor na folha
   juntada refaz a conta (a mesma da folha nunca dividida) e grava a linha nova na mesma ação do desfazer. "dividir
   esta" depois corta nela e devolve as páginas de antes (D-498). Se o motor novo achar a folha de uma página só, a
   linha some (como na folha nunca dividida) e o "dividir esta" usaria a conta forçada.
   Arquivo: `ui/tela_conferir.py` (`_trocar_jeito_da_folha`, `_linha_com_o_motor`).
2. **D-607, o aviso.** Texto exato quando só há folhas juntadas:
   > 70 páginas foram juntadas no Dividir e vão ser separadas se o processar continuar nelas. Pular essas páginas?

   Uma só: "1 página foi juntada no Dividir e vai ser separada se o processar continuar nela. Pular essas páginas?"
   Mistura (3 juntadas e 1 mexida de outro jeito):
   > 3 páginas foram juntadas no Dividir e vão ser separadas se o processar continuar nelas. 1 página foi mexida à mão nas etapas que vão rodar. Pular essas páginas?

   Sem juntadas: o texto de sempre, letra por letra. Botões "Pular as N" / "Rodar nelas também" / "cancelar" e a
   explicação de baixo, iguais. "Juntada" = folha não dividida que guarda as duas páginas de antes ("não dividir
   esta" ou "juntar todas") e o pedido tem o Dividir. Arquivos: `core/automatico.py` (`paginas_juntadas`),
   `ui/janela_principal.py` (`texto_das_mexidas`, `_perguntar_mexidas`).
3. **Setas depois da lista "motor de corte".** A lista pegava o teclado ao ser clicada. Agora não pega (como as
   outras listas da área de trabalho). No Gradus: → da folha 6 para a 7, troca do motor na 7, → foi para a 8, ← voltou
   à 7 (p01). Arquivo: `ui/tela_conferir.py` (uma linha).
4. **Tira depois do Ctrl+Z.** A tira rolava antes de os quadros novos estarem no lugar e caía no começo. Agora rola
   de novo quando estão. Gradus: folha 60, Ctrl+Z do "dividir todas" → miniatura 60 à vista (p05); refazer →
   miniatura 119 (folha 60) à vista (p06). Arquivo: `ui/widgets/tira_miniaturas.py`.
5. **"7 com dúvida" — não é defeito, nada mudou.** São os avisos "Parece em branco" das metades esquerdas que são
   páginas em branco no livro: folhas 2, 3, 7, 8, 62, 63 e 69 (páginas 3, 5, 13, 15, 123, 125, 137 depois de dividir).
   Desfazendo e dando "dividir esta" só nessas 7 folhas, saem os mesmos 7 avisos, nas mesmas metades. Ao abrir o livro,
   0 dúvidas (a folha inteira não tem página branca). Print da folha 7 (metade esquerda branca, "7 com dúvida"): p04.
6. **Etapa 6 cortada.** A janela principal de 1536 x 824 abre a do Automático com 92% (1413 x 758): a coluna do meio
   tinha 674 pontos e a linha "página menor, de cima a baixo: [no meio] de um lado ao outro: [no meio]" pedia 732.
   Agora essa linha dobra em duas só quando não cabe (mesmos textos, controles e ordem); onde cabe (janela de 1536
   de largura) fica numa linha, como era. Medido na janela de verdade: rolagem de lado 58 → 0 (p08).
   Arquivo: `ui/automatico.py` (`_LinhaQueDobra`, `_opcoes_margens`).

## Testes

- Testes de reversão (todos falham no código de `75ed04af` e passam no novo): D-606 (2), D-607 (3 de 4; o 4º é a
  guarda "sem juntadas, texto de sempre"), setas, tira, etapa 6 (`tests/test_dividir_ajustes_03_11.py`; mais uma
  guarda: onde cabe, a linha fica como era).
- PC, um arquivo por vez: RESULTADOS_PC
- GitHub: RESULTADOS_GH

## Ressalvas

- Item 1: a linha "acertada à mão" da folha 5 (0,44) foi posta pelo sinal da linha (como o arrastar), não com o
  mouse; o resto foi clique e tecla do Windows.
- Item 2: página que é de folha juntada e também foi mexida de outro jeito entra na parte das "juntadas" (a soma das
  duas partes é sempre a contagem dos botões). A palavra "processar" é a do Samuel; o botão da janela diz "Rodar".
- Item 3: a lista não pega mais o teclado. Mas os **botões** do painel ("dividir esta", "não dividir esta", "juntar
  todas", "dividir todas", "usar em todas" — e os das outras ferramentas, como "não cortar esta") ainda pegam: depois
  de clicar num deles, a seta passa de um botão a outro em vez de trocar de folha. Na sequência do verificador ele
  tinha clicado nesses botões antes da lista. Não consertei (é de todas as ferramentas, vai como pergunta/bug).
- Item 5: no Dividir a faixa da folha 7 mostra a frase do Dividir, não o "Parece em branco" (o aviso é da página e
  aparece no "Para revisar" e nas outras ferramentas). Isso já era assim.

## Bugs para a Lista de bugs (não consertados)

- 03/11/2026, Dividir: depois de **refazer** (Ctrl+Y) o "dividir todas", os 7 "Parece em branco" somem (contador
  0 com dúvida); antes do Ctrl+Z eram 7. O refazer devolve as páginas como estavam na hora do corte, antes da
  medida do em branco por trás, e não mede de novo. Anotações em `anotacoes.txt` ("depois do refazer").
- 03/11/2026, todas as ferramentas: botão do painel clicado fica com o teclado e as setas passam a andar entre os
  botões (ver ressalva do item 3).

## Prints (pasta `relatorios/dividir-ajustes/`)

- p01 — item 3: depois de trocar o motor na folha 7, a seta → foi para a folha 8.
- p02 — item 1: folha 5 juntada, linha de antes (0,44), motor "o do ScanTailor".
- p03 — item 1: a mesma folha com o motor "o do Editor": linha em 0,5033.
- p04 — item 5: folha 7 depois do "dividir todas", metade esquerda em branco, "7 com dúvida".
- p05 — item 4: folha 60 depois do Ctrl+Z, a miniatura 60 escolhida e à vista.
- p06 — item 4: depois do refazer, a miniatura da folha 60 à vista.
- p07 — item 2: o aviso novo depois do "juntar todas" (70 páginas).
- p08 — item 6: a etapa 6 inteira, janela do Automático aberta da janela de 1536 x 824.
