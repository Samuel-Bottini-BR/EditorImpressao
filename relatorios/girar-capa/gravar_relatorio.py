"""Grava o relatório do girar com a capa aberta (D-638, D-640) nos três formatos (relatorio.gravar).

    python relatorios/girar-capa/gravar_relatorio.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1]))
import relatorio  # noqa: E402

TEXTO = r"""# Girar num livro dividido com a capa aberta inteira (D-638 e D-640)

Ramo `girar-capa-2026-11-07` (saiu do `obra-2026-10-26`). Teste de **máquina** (provas automáticas e medidas do PDF)
e de **olho** (as imagens, para o Samuel conferir). PRONTO PARA A CONFERÊNCIA COM A JANELA ABERTA (outro agente).

## O defeito, em frases simples

1. **Na capa aberta**, girar com "todas as folhas" (ou "daqui em diante", "só as pares", "só as ímpares") girava também
   as folhas divididas como folha inteira. Cada página delas virava uma tira com pedaço da vizinha (a confusão do
   print a-70), e o PDF saía assim.
2. **No miolo**, girar com "todas as páginas" deixava a capa aberta sem girar.

## O que mudou

1. Na capa (folha inteira): as folhas não divididas giram inteiras, como antes; as divididas giram página por página,
   cada uma sozinha, sem pedaço da vizinha. Todas ficam viradas como a capa. Com ou sem o corte das bordas.
2. No miolo, "todas as páginas" gira também a capa aberta, inteira (como uma foto, levando o corte à mão).
3. Um Ctrl+Z desfaz tudo de uma vez; Ctrl+Y refaz.
4. Não mudou: "só esta", os botões do canto, o menu, a grade "ver todas", as palavras do quadro, o aviso de
   pares/ímpares, e o giro num livro sem folha dividida.

## As imagens (Gradus Primus, cópia; janela desenhada na memória, nada abriu na tela)

- `s1-pdf-antes-e-depois.png`: na capa, "todas as folhas" + ¼ à esquerda. Código de antes: as páginas 2, 3, 14 e 15
  saem como tiras em pé com metade da folha (a 2 mostra o título que é da 3; a 14 mostra a águia que é da 15). Código
  novo: cada página deitada, inteira, com o seu conteúdo; a capa em pé.
- `s2-pdf-antes-e-depois.png`: na página 14, "todas as páginas" + ¼ à esquerda. Código de antes: a capa sai igual,
  sem girar. Código novo: a capa sai girada, como as outras.
- `s1-janela-antes-e-depois.png` e `s2-janela-antes-e-depois.png`: a janela no mesmo caminho.

Caminho das imagens: livro novo com os ajustes de fábrica (endireitar e cortar as bordas desligados, filtro Original),
folhas 2 a 70 divididas pela lombada, folha 1 inteira, ferramenta Cortar as bordas. O PDF com o corte das bordas
ligado foi conferido pelas provas automáticas (`[True]`).

## Testes

- Prova de reversão: `tests/test_decisoes_girar_capa.py` (19 provas) no código de antes: 15 falham pelo defeito
  (ex.: "assert [270, 270, 270, 270] == [270, 270, 0, 0]": as folhas divididas giravam como folha); 4 passam (as que
  conferem o que não pode mudar). No código novo: 19 passam.
- PC, um arquivo por vez: 70 arquivos; 68 passam inteiros. Falham 5 testes antigos que cobram justamente o
  comportamento que o Samuel mandou trocar (a capa não girar com "todas as páginas"; as folhas divididas girarem
  como folha). Não foram mudados; a proposta está em `proposta-testes-d636.diff` e foi conferida numa cópia à parte.
- GitHub, suíte 42381756807: só esses 5 falham. Velocidade: ver o ONDE-PAREI.

## Segunda parte (07/11): as respostas do Samuel na Central

- "Posso trocar os 5 testes antigos?" → "Sim, pode trocar (recomendo)": trocadas só aquelas linhas (16e752e7).
- "No miolo, "daqui em diante", "só as pares" e "só as ímpares" giram também a capa aberta?" → "Giram também": feito
  (df8db4ec). A folha inteira cuja página está no grupo escolhido gira também, inteira, virada como a página da vez.
  Par/ímpar pelo número da página que a tela mostra (a capa é a página 1, ímpar). Imagens: `s3-*.png`.
- Mais um teste antigo cobra o jeito de antes (o "daqui em diante" com uma folha inteira depois da página da vez): não
  foi trocado, falta autorização (proposta em `proposta-teste-daqui.diff`).
- PC: 70 arquivos, 69 passam inteiros; falha só esse teste. GitHub 42391132998: esse teste e o instável conhecido
  `test_d148` (passa no PC).

## Ressalvas

- Os 5 testes antigos só passam se a gerente autorizar a troca das linhas (decisão nova do Samuel contra prova
  provisória).
- "daqui em diante", "pares" e "ímpares" no miolo continuam sem girar a capa (a D-640 fala de "todas as páginas"):
  pergunta 1.
- Dividir em "Duas lado a lado" numa folha dividida: continua como antes (pergunta 2).
- A janela foi desenhada na memória; a conferência com a janela aberta fica para outro agente.
"""

if __name__ == "__main__":
    print(relatorio.gravar(TEXTO, AQUI / "relatorio", "Girar com a capa aberta (D-638, D-640)"))
