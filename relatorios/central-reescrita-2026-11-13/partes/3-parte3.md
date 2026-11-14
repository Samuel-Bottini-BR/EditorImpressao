## Parte 3: as abas de auditoria (141 perguntas mudaram)

Arquivos: `novas/auditoria-3-com-ressalva.json` (31 das 32), `novas/auditoria-4-funciona.json` (88 das 92),
`novas/auditoria-5-escolhas-da-gerente.json` (16 das 19), `novas/auditoria-6-para-depois.json` (6 das 13). As que
ele já respondeu (15) ficaram iguais, letra por letra (conferido por script). O resumo de cada aba foi reescrito.

**Motivo (para todas):** as fichas "Situação / Você pediu / O que isso quer dizer / Solução na versão de teste / Parte
do programa / Ressalva" são, nas palavras da regra nova, as que mais voltaram com "Ainda não entendi" (CLAUDE.md
§11.13, regra 7: "Nada de ficha com campos"). Os comentários dele que motivaram a regra: "Um monte de texto e não
consigo saber o que era para saber realmente" · "os relatorios continuam muito ruins e dificeis de entender" · "nos
para responder, não tem explicações sobre o que precisa ser respondido".

**O que mudou em cada uma (o mesmo molde para as 141):**
1. **Onde fica e o que é**, numa frase só ("Onde fica: Dividir as folhas. O que é: ...").
2. **O que ele pediu, com a data e as palavras dele.** Quando a ficha dizia "Você pediu" mas era "(escolha da
   gerente, D-014)", agora diz com todas as letras: "ninguém perguntou a você; a gerente escolheu sozinha em 27/10"
   (regra 9). Isso acontecia em várias da aba 4 e da aba 6, não só na aba 5.
3. **Como está hoje** na versão de teste e, quando havia ressalva, "O que ainda não está bom".
4. **Se ele já testou depois da auditoria de 29/10**, procurado no Livro de decisões (ver a lista abaixo).
5. **O que ele escolhe**, com as mesmas opções (ids iguais), e o texto de cada opção dizendo o que acontece.
6. O número da decisão só no fim, "(Para consulta: D-xxx)".

**Palavras de dentro tiradas** (por script, `scripts/parte3.py`, função `limpar`, e conferidas por busca no
resultado): números de decisão no meio do texto (viraram "a decisão de 05/10"), códigos de pergunta e de rodada
("G2:", "P6:", "F5", "R7 203 D", "904 A", "rv4-...", "dv-..."), números de item do plano ("2.13", "1.6/2.10",
"item 7.3"), "etapa 9b-2", "obra", "junção", nomes de arquivo e de função, "escolha da gerente" como rótulo. Os
títulos que vinham cortados com "…" foram refeitos (à mão; os outros pela primeira frase do "o que é"). A busca
final não acha mais nenhum desses códigos nos textos reescritos ("A4" é o papel e ficou).

**O que não mudou:** as imagens (são as que já existiam, prints de quando o assunto foi decidido; a tarefa não pedia
print novo aqui); as palavras dele entre aspas (só tirei os códigos que vinham grudados nelas).

**Ressalva desta parte:** o texto é montado por script a partir das fichas antigas e do Livro, com 32 títulos e 22
explicações ou pedidos reescritos à mão. Li as 141 por amostra e por busca de padrões estranhos, não uma por uma com o mesmo
cuidado das Partes 1 e 2. Algumas explicações continuam compridas porque a decisão é comprida (ex.: a ferramenta
Mover). A gerente pode querer encurtar essas antes de publicar.

### Já testado ou já respondido por ele depois da auditoria (o que achei no Livro)
- **Testado em parte (ficam na lista, com a frase "Já testado por você" dizendo o que falta):** au-d-021 (setas,
  10/11 "sim"), au-d-334 e au-d-487 (o "inserir" virou "adicionar página em branco", 09/11 "pagina em branco
  funciona"), au-d-568 (Ctrl + roda 01/11 "1- funcionando"; Shift + roda 02/11 "shift funcionando"), au-d-373 e
  au-d-007 e au-d-090 (Dividir testado em 10/11, "ok"), au-d-168 (caixinha irmã testada em 29/10), au-d-095 (cantinho
  do giro, 10/11: "a cor é diferente da cor do papel").
- **Não achei teste dele no Livro** para as outras 124. O Livro pode não ter anotado algum teste feito no chat;
  quando é assim, a pergunta diz "Você ainda não testou isto depois da auditoria de 29/10 (não há teste seu no Livro
  de decisões)".

