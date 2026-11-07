"""Grava o relatorio da tarefa da cunha na pagina segurada (06/11/2026) nos
tres formatos (relatorio.gravar: .md, .html, .pdf). Uso:
.venv\\Scripts\\python.exe relatorios\\cunha-desentortar\\gravar_relatorio.py "<texto da velocidade>"
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

import relatorio  # noqa: E402

VELOCIDADE = sys.argv[1] if len(sys.argv) > 1 else "(ainda rodando)"

TEXTO = f"""# Cantinho do giro com a cor do papel também na página segurada pelo Desentortar

06/11/2026 · ramo `cunha-desentortar-2026-11-06` · teste de **máquina** (medida) + antes/depois para o **olho** do Samuel.

## O que mudou, em uma frase

Com o "Desentortar" ligado, quando o programa não consegue desentortar a página (aviso "Desentortar não usado"),
a lasca fina que o giro abre na beirada saía **branca**; agora sai **da cor do papel**, igual à página com o
Desentortar desligado. O aviso continua aparecendo na mesma página.

## A foto

`destino18-direita-antes-depois.png`: Destino do socialismo, p. 18, página da direita, canto de cima à esquerda, ampliado 5 vezes.

Caminho: livro novo de fábrica, dividida (página da direita), endireitada, cortada, Desentortar automático
(a proteção segurou: aviso "Desentortar não usado"), filtro Original. Desenhada na resolução do livro (300 DPI), o mesmo desenho do PDF.

- Antes: lasca branca na beirada esquerda (13674 pontos branco puro nos 12 pontos da esquerda). Aviso: sim.
- Depois: a lasca com a cor do papel (0 pontos brancos). Aviso: sim.
- Referência, Desentortar desligado: 0 pontos brancos. A página "depois" é igual a ela (0 valores diferentes em mais de 64 tons; antes eram 2292).

## Decisões

- D-095 (12/10): "cunhas brancas com corte até a beirada" -> consertado também com o Desentortar ligado.
- D-639 (06/11): "pode consertar o triangulo" -> a cor é a mesma conta de antes (a mediana do papel de dentro do corte), nunca a cor do fundo atrás da folha.
- D-105 / D-108 (22/10): a proteção segura a mesma página e o aviso aparece: o desentortar recebe exatamente a mesma página de antes; só a página que sai é trocada.

## Testes

- Reversão: prova nova em `tests/test_decisoes.py` falha no código antigo (27% de branco nas beiradas) e passa no novo;
  o teste do Destino 18 falha no antigo (`2292 == 0`) e passa no novo.
- PC, um arquivo por vez: todos passando (ver ONDE-PAREI).
- GitHub: suíte 42315842817, tudo verde.
- Velocidade: {VELOCIDADE}

## Ressalvas

- A página **desentortada de verdade** (a proteção deixou passar, ou "Desentortar aumentando a página") não foi mexida:
  se tiver cantinho, ele continua branco. O Livro não decide isso; fica como pergunta.
- Se o desentortar não conseguir rodar (a peça do ScanTailor faltando), a página sai sem desentortar e sem aviso, e o
  cantinho continua branco. Não está no pedido; fica como pergunta.
- Projeto começado antes de 09/10: não muda (lá o caminho desligado também deixa o cantinho branco, idêntico ponto por ponto).
- Antes de a medida por trás terminar, a prévia rápida mostra a página sem desentortar com o cantinho branco por alguns segundos; o PDF não.
- Não abri a janela do programa: medi no desenho do PDF (`renderizar_pagina` na resolução do livro).
"""

if __name__ == "__main__":
    print(relatorio.gravar(TEXTO, Path(__file__).parent / "RELATORIO",
                           titulo="Cantinho do giro na página segurada pelo Desentortar"))
