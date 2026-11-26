# Prova à vista do atualizador novo: o resultado

Feita no PC do Samuel em 25 e 26/11/2026, das 19h20 à 1h10, com as versões de prova 1.9.0 a 1.9.6, publicadas numa
pasta do computador (nunca no GitHub). O Samuel clicou no programa; a gerente preparou cada passo e conferiu por fora (o
registro do atualizador, a pasta do programa e a vigia das janelas).

**Em uma frase:** o atualizador fez o que devia em todos os passos. A prova achou um caso de dois programas abertos
(o clique no atalho no fim da troca) e dois defeitos fora do atualizador, todos anotados abaixo.

## O que funcionou, passo a passo

| Passo | O que se fez | O que aconteceu |
|---|---|---|
| 1 | Instalar a 1.9.0 | Instalou, deixou tudo preparado e pôs o motor de achar texto no lugar. A caixinha do instalador "abrir o programa" ficou marcada, então a pergunta do Windows não apareceu: o caminho do "Não" nessa pergunta **não foi visto**. |
| 2 | 1.9.1 publicada, "Reiniciar agora" | O aviso apareceu com o texto certo; trocou, passou no teste e ficou guardada, sem internet. Na abertura seguinte não testou de novo. |
| 3 | 1.9.2, "Depois", fechar, "Não" | Ao fechar perguntou "Atualizar agora?"; com "Não", o aviso voltou na abertura seguinte. |
| 4 | 1.9.3, que não abre | O teste da versão nova falhou: a caixa do Windows apareceu uma vez, e não apareceu de novo; a versão não foi testada de novo. A volta à mão para a 1.9.2 levou 11 s e o programa abriu normal; a 1.9.3 não foi mais oferecida. |
| 4 | 1.9.4 (a correção), "Depois", fechar, **"Sim"** | Trocou ao fechar, passou no teste sem abrir janela e ficou guardada. |
| 5 | 1.9.5 com a assinatura falsa | A caixa "Atualização" ("não tem a assinatura do Samuel") apareceu uma vez; nada baixado; na abertura seguinte, nada. |
| 7 | Motor de achar texto fora do lugar, 1.9.6 publicada | Nenhum aviso, nenhuma pergunta; nada procurado. |
| 6 | "Internet" parada com a 1.9.6 já baixada | O aviso apareceu mesmo assim. |
| 9 | Atualizador do Velopack apagado, "Reiniciar agora" | A caixa "o atualizador do programa sumiu do computador" (texto certo, palavra por palavra); o programa continuou aberto até o X; ao fechar, nenhuma pergunta. |
| 10 | Pasta do programa presa, "Reiniciar agora" duas vezes | As duas vezes: a caixa "A atualização não deu certo", o programa de volta na 1.9.4 e o aviso de novo. |
| 8 | Clique duplo no atalho durante a troca | O primeiro clique (antes de os arquivos serem trocados) saiu sem janela, como devia. O segundo abriu outro programa (ver os achados). |
| 11 | Desinstalar | A pasta do programa sumiu inteira, a entrada saiu da lista do Windows, o atalho saiu da área de trabalho. Uma pergunta do Windows. |

## Quanto a abertura leva

De o processo começar até a janela principal aparecer, lido da vigia: **de 10 a 23 s** nas aberturas comuns, com e sem
versão nova sendo baixada por trás (o vai-e-vem é do PC, não do atualizador). Depois de uma troca, a primeira abertura
leva **de 30 a 36 s**, porque o teste da versão nova roda antes (de 12 a 22 s) ou porque espera o OK de uma caixa.

## Os achados

1. **Dois programas abertos (a conferir).** No clique duplo do passo 8, o segundo clique veio quando os arquivos já
   estavam trocados, mas o Velopack ainda não tinha terminado: abriu um programa, e a reabertura do Velopack abriu
   outro. A causa: o programa só confere se o Velopack está trabalhando quando a versão que roda é diferente da última
   boa, e a volta à mão feita na prova tinha deixado a 1.9.6 como última boa. No uso normal a conferência seria feita
   (lido no código, não visto na tela). **Mas há um caso parecido no uso normal, também só lido no código:** nos 12 a
   22 s em que o teste da versão nova roda, não há nada na tela; se o Kaique clicar no atalho nesse tempo, o programa
   abre, e o teste abre outro. Precisa de prova.
2. **A janelinha do Velopack tem um botão OK** ("Instalando Atualização"). O Samuel perguntou "tem um ok aqui, se eu
   apertar o que acontece?": só fecha a janelinha, a troca continua. O Kaique pode ter a mesma dúvida.
3. **Uma caixa técnica em inglês** ("Unhandled exception in script", do PyInstaller) apareceu na versão que não abre
   (1.9.3), depois do botão da caixa "Um momento". Fere a regra de nunca mostrar erro técnico. Vai junto com o item da
   frase quando a janela não abre, que o Samuel deixou para depois da entrega.
4. **Fora do atualizador: dois projetos mudam de data ao abrir o programa.** Os resumos de "Schön Neues Modell Buch" e
   de "Sobre a Consolação da Filosofia" foram regravados às 00:45:08 (o conteúdo igual, só o "mexido em" mudou, e isso
   muda a ordem da lista). As duas pastas têm acento no nome e não têm a capa (`capa.png`); provável causa: o programa
   tenta criar a capa a cada vez, a gravação da imagem falha no caminho com acento, e o resumo é gravado do mesmo
   jeito. Nada sumiu nem mudou dentro dos projetos além disso. Não tem relação com desinstalar.
5. **O Velopack tenta a troca por uns 15 s, não 1 minuto** como o roteiro dizia. Não é defeito do programa; a tranca
   da pasta precisou ser renovada entre as duas recusas.

## O que não foi visto

- O "Não" na pergunta do Windows na primeira abertura (passo 1).
- O segundo clique no atalho no uso normal (achado 1).

Opinião da gerente: o atualizador está pronto para a entrega no que a prova cobriu. O achado 1 é o único que o Kaique
pode encontrar sozinho; na prova ele só abriu dois programas, mas não se sabe o que acontece se o Kaique mexer no mesmo
livro nos dois. A decisão de consertar antes ou
depois da entrega é do Samuel.
