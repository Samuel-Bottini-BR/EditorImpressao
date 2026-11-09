"""Grava o relatório das provas das perguntas 3 e 4 do girar-capa nos três formatos (relatorio.gravar).

    python relatorios/girar-capa-provas/gravar_relatorio.py

As imagens saem de gerar_provas.py (no programa, sem janela na tela) e montar_provas.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1]))
import relatorio  # noqa: E402

TEXTO = r"""# Provas das perguntas 3 e 4 do girar (Gradus Primus)

09/11/2026 · Gradus Primus **copiado** (70 folhas), pasta de dados só destas provas · o programa rodou **sem
janela na tela** (desenhado na memória) · as fotos são do próprio programa. Teste de **olho**: PRONTO PARA CONFERIR.

## Pergunta 4 — o teste antigo do "daqui em diante"

Livro: folhas 2 a 70 divididas, menos a folha 4 ("não dividir esta"), que virou a **página 6, inteira**
(circulada em vermelho). Clique: na página 3, "daqui em diante" + ¼ à direita.

1. O teste antigo cobra o **jeito antigo**: as páginas 3, 4, 5, 7 e 8 deitam, mas a folha inteira (página 6) fica em pé.
2. Com a sua resposta "Giram também", a página 6 **gira junto** com as outras (jeito novo).
3. Por isso esse teste antigo falha no programa novo; trocar uma linha dele faz ele cobrar o jeito novo.

![Resumo da pergunta 4](q4-resumo.png)

**Miniaturas (tira do programa):**

![ANTES do clique](q4-1-miniaturas-antes.png)

![DEPOIS — jeito antigo](q4-2-miniaturas-antigo.png)

![DEPOIS — jeito novo](q4-3-miniaturas-novo.png)

**As páginas como saem no PDF:**

![ANTES do clique](q4-4-pdf-antes.png)

![DEPOIS — jeito antigo](q4-5-pdf-antigo.png)

![DEPOIS — jeito novo](q4-6-pdf-novo.png)

## Pergunta 3 — Dividir com "Duas lado a lado"

Livro: folhas 2 a 70 divididas (a capa inteira). Ferramenta Dividir, vista "Duas lado a lado", folha 10
(páginas 18 e 19, em vermelho). Clique: "todas as folhas" + ¼ à direita.

1. **"Fica como está"**: as folhas giram inteiras e a linha azul fica no mesmo lugar; no livro impresso, cada página
   sai como uma tira estreita com metade de duas páginas misturadas (a confusão do print a-70).
2. **"Página por página também"** (simulação, ainda não existe no Dividir): no livro impresso, cada página sai
   inteira, sem pedaço da vizinha (deitada, porque o clique foi ¼); a tela grande do Dividir continua mostrando a
   folha em pé, só as miniaturas mudam.
3. Nas duas opções a capa (folha inteira) gira inteira.

![Resumo da pergunta 3](q3-resumo.png)

![ANTES do clique](q3-1-antes.png)

![DEPOIS — "Fica como está"](q3-2-fica.png)

![DEPOIS — "Página por página também" (simulação)](q3-3-pagina.png)

## Ressalvas

- O "Página por página também" é uma **simulação**: o resultado foi feito pelo caminho que já existe (Cortar as
  bordas, página 18, "todas as páginas", D-636). A foto da tela do Dividir nessa imagem é a tela de hoje com esse
  resultado; se o jeito for feito no Dividir, essa tela pode mudar.
- O Dividir com **"Uma página"** já gira página por página hoje (ali a lista diz "todas as páginas").
- A cópia do Gradus da conferência anterior (`testa-girar-capa\saida_teste\livros\gradus.pdf`) tem as folhas
  deitadas; usei uma cópia nova do Gradus da Área de Trabalho (folhas em pé), como o relatório do girar-capa.
- "jeito antigo" = código `6904a634` (sem o conserto); "jeito novo" = `girar-capa-2026-11-07` (`80696770`).
  Os números de cada clique estão em `estado-*.json`. Nada diferente do que o relatório do girar-capa dizia.
"""

if __name__ == "__main__":
    print(relatorio.gravar(TEXTO, AQUI / "relatorio", "Provas das perguntas 3 e 4 do girar"))
