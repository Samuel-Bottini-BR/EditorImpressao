"""Grava a página de conferência da etapa 10b nos três formatos (relatorio.gravar).

USO (da pasta da worktree): python relatorios/obra-etapa10b/scripts/fazer_conferencia.py
As fotos ficam em relatorios/obra-etapa10b/conferencia/img/ (fazer_imagens.py).
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[2]))

from relatorio import gravar  # noqa: E402

TEXTO = """# Etapa 10b da obra: defeitos na imagem final — antes × agora

**PRONTO PARA CONFERIR** (27/10/2026). Ramo `obra-etapa10b-2026-10-26`. Teste de **olho** (as fotos) e de **máquina**
(`tests/test_etapa10b_imagem.py`: cada defeito tem uma medida que falha no código de antes e passa no de agora).

O critério do Samuel: *"Eu quero que o papel saia branco, e o desenho também saia perfeito."*

Cada foto diz por onde a página passou e com quais opções. "Antes" = o programa de hoje (`ab38208`); "Agora" = esta
etapa. Só páginas que vão ser impressas.

---

## 1. Gravura estragada no Preto e branco (lista única 4.1)

Palavras do teste dos livros: *"No Palatino 74 [...] o fundo virou chuvisco preto e branco com manchas pretas grandes;
no Valadés 41 [...] o traço fino virou áreas pretas chapadas e os rostos perderam detalhe."*

**O que olhar:** as manchas e áreas pretas chapadas sumiram. **O que mudou:** a mancha escura pequena da gravura era
enchida de preto inteira; agora só o que é tinta de verdade fica preto.
Medida: bloco preto onde o original não é tinta cheia — Palatino 74: 1,4% da página → 0,003%; Valadés 41: 2,0% → 0,05%.

![](img/4-1-palatino74.jpg)

![](img/4-1-valades41.jpg)

![](img/4-1-siebmacher110.jpg)

**Ressalva:** o fundo manchado da gravura em madeira (Palatino 74) continua "chuviscado": em preto e branco puro ele só
sai assim. Em tons de cinza (como as fotos) ele fica igual ao original — **pergunta 3** abaixo. No Siebmacher 110 o
detector acha só parte do bordado; o resto é tratado como texto.

---

## 2. Folha branca sai cinza e manchada (lista única 4.3)

Palavras: *"Uma folha de guarda branca sai cinza e toda manchada: a textura e as rugas do papel viram desenho
(Boécio 49, Marial 2)."*

**O que olhar:** o papel da folha de guarda sai branco; o carimbo do Marial 2 continua. Medida (Boécio 49): mediana
189 → 238; parte da página abaixo de 200: 65% → 6%.

![](img/4-3-boecio49.jpg)

![](img/4-3-marial2.jpg)

![](img/4-3-siebmacher74.jpg)

**Ressalva:** o Marial 2 é um papel amassado de verdade: as rugas ficam claras, mas aparecem. No Siebmacher 86 o
desenho muito fraco some no Preto e branco (já era assim; o borrão preto não volta).

---

## 3. Matemática 40 e 66: o Preto e branco apagava o texto perto da lombada

Palavras: *"Matemática 66 (e 92): cada número de questão com sombreado cinza virou borrão preto. Matemática 40 (e
118): as primeiras letras de cada linha, perto da lombada, sumiram ('Suponha que' → '~cha que')."* A etapa 10a provou
que o corte estava certo; o defeito era do Preto e branco na sombra da lombada.

**O que olhar:** na 66 a faixa preta da esquerda sumiu e os números voltaram; na 40 as primeiras palavras voltam (como
borrões escuros, porque no original elas também estão borradas). Medidas: 66, faixa da esquerda preta 4,7% → 0,3%;
40, tinta na faixa da sombra 7,1% → 13%.

![](img/4-2-matematica66.jpg)

![](img/4-2-matematica40.jpg)

---

## 4. Foto de celular: a sombra virava mancha preta (Lista de bugs, 23/10)

*"Páginas fotografadas (celular): o Preto e branco transforma a sombra da mão ou da página numa grande mancha preta."*

**O que olhar:** a sombra da esquerda (Razões) e a da mão (Atanásio) não viram mais mancha preta.

![](img/celular.jpg)

---

## 5. Retângulos brancos no cartão das pranchas da Pesel (lista única 4.7)

*"O bordado ficou bom, mas o cartão marrom em volta virou um remendo: o título e cada bloco de texto ganharam um
retângulo branco por cima, com a letra engrossada, e sobrou uma tira branca torta na beirada esquerda."*

**O que olhar:** o cartão fica marrom inteiro, com o título e o texto como no original. Medida (Pesel 51): parte do
cartão que saía branca 32% → 5%.

![](img/4-7-pesel51.jpg)

![](img/4-7-pesel67.jpg)

**Ressalva:** no Pesel 51 sobra uma cunha clara fina entre o título e a prancha.

---

## 6. Mancha vira ponto preto (4.11) e pontinhos laranja (4.12)

*"Valadés 203: uma mancha marrom pequena em cima de uma palavra virou um ponto preto em cima de 'Idiomate'."* ·
*"Antiphon 56: sobraram pontinhos laranja das manchas do pergaminho na margem da direita."*

**O que olhar:** o ponto preto saiu (fica um pedacinho onde a mancha é tão escura quanto a tinta); os pontinhos
laranja da margem saíram (2.656 → 183). O retângulo cinza do Antiphon é o 4.6 (outra etapa).

![](img/4-11-valades203.jpg)

![](img/4-12-antiphon56.jpg)

---

## 7. A letra T do Antiphonal 46: a tela mostrava, o PDF não tinha (Lista de bugs 13/10, grave)

*"No 'Só as letras', a tela mostra o que o PDF não tem."* Decisões: *"precisamos que o pdf saia que nem está na tela"*
(D-066) e "Tela e PDF saem da mesma conta" (D-473).

**O que olhar:** a T aparece na tela e no PDF. A conta que decide o que fica passou a ser a mesma nos dois tamanhos.

![](img/t-antiphonal46.jpg)

---

## 8. Tela cheia com a letra mais grossa que o PDF (`lu-tc-igual`, D-193)

*"O pdf está saindo diferente da tela gerada, na tela gerada a letra está mais grossa, isso é um perigo [...]"*

**O que olhar:** na tela cheia a letra tem agora a grossura do PDF (antes 10 a 17% mais grossa; agora 4 a 9% mais fina,
porque a tela é preto e branco em 150 DPI). Para ficar igual de verdade falta a tela trocar sozinha pela imagem do PDF
(a parte de tela, com as duas bolinhas, fica com a gerente).

![](img/tela-cheia-boecio22.jpg)

---

## 9. "Reduzir cores" apagava a letra (D-189)

*"Ele está apagando as letras [...]"* · *"aprovado, mas ainda tem que melhorar, em alguns casos, ele acaba apagando a letra."*

**O que olhar:** com "Reduzir cores", cada palavra fica inteira numa cor só (antes, metade preta e metade clara).
Medida: letras que viravam preto 20% → 0,1%.

![](img/reduzir-cores-horas26.jpg)

---

## 10. PDF gigante (lista única 4.5)

*"Com Mágico pro e Melhorar o PDF sai de 15 a 20 vezes maior que o original [...] Difícil de guardar, copiar e mandar
para a gráfica."*

A causa: o programa guardava cada página de cor sem perda nenhuma, com todo o grão do scan. Agora vai em JPEG de
qualidade alta (92). O PDF fica **1,4 a 10 vezes menor** (Antiphon 56: 20 MB → 4 MB por página; o livro de 1.590 MB
iria para ~330 MB). A diferença para a imagem de antes é de 1 a 3 tons de 255 (não se vê). O Preto e branco puro
continua sem perda. Tabela completa no ONDE-PAREI. **Pergunta 2** abaixo (dá para ficar 2 a 4 vezes menor ainda).

---

## 11. Desentortar só no bloco do texto (D-493)

**O que olhar:** com "Desentortar aumentando a página", seguindo só o bloco do texto, a página curva sai com as linhas
mais retas (à direita). **Mas não liguei** para todo livro: ligado, entortava uma página reta (Marial 41) e cortava o
começo das linhas do Righetti 96. **Pergunta 1** abaixo.

![](img/d493-desentortar.jpg)

---

## 12. O que mudou nas páginas-gabarito (somas)

Original: nada mudou (32 de 32). Preto e branco: mudam as páginas com sombra na beirada ou com gravura (diferenças
pequenas). Melhorar: mudam todas, pouco (o grão do papel); o Opus 20 muda mais: o vão escuro atrás da estátua deixou
de ter os pontinhos brancos (a queixa *"esses pontos estão horríveis atrás da estátua"*, conferência 6).

![](img/somas-opus20-melhorar.jpg)

![](img/somas-graduale222-pb.jpg)

![](img/somas-marial7-melhorar.jpg)

---

## Perguntas para o Samuel

1. **Desentortar só no texto:** recomendo **não ligar para todo livro** e oferecer como opção da página ("Desentortar
   seguindo só o texto, sem as notas da margem"), para as páginas curvas com notas na margem.
2. **PDF menor:** recomendo **ficar com o JPEG 92** e, nos livros de página grande escaneada em resolução baixa (Horas,
   Antiphon, Graduale, ljs47), **guardar a página com no máximo 2 vezes a resolução do scan** (nada do scan se perde; o
   PDF fica mais 2 a 4 vezes menor).
3. **Gravura de fundo escuro no Preto e branco:** sai em **tons de cinza** (como as fotos, igual ao original) ou continua
   em preto e branco puro (com chuvisco no fundo manchado)? Recomendo tons de cinza para ela.

## Opinião do implementador

Os defeitos da lista saíram nas páginas apontadas, com medida antes e agora e teste que pega a volta. O que não ficou
perfeito está nas ressalvas e nas três perguntas. Quem confere é o Samuel.
"""


def main() -> None:
    destino = AQUI.parent / "conferencia" / "conferencia-etapa10b"
    print(gravar(TEXTO, destino, titulo="Etapa 10b — defeitos na imagem final"))


if __name__ == "__main__":
    main()
