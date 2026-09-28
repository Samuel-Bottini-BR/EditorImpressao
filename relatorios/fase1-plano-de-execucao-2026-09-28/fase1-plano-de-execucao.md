# Fase 1: plano de execução (28/09/2026)

Escrito pela conversa gerente. **Regra de trabalho (Samuel, 28/09):** cada item termina como PRONTO PARA CONFERIR, com relatório de antes/depois em `relatorios/`; cada item é um commit separado no ramo `fase-1` (com cópia no GitHub); o ramo principal só recebe o que o Samuel aprovar.

## A ordem

1. **Lista de bugs (em andamento).** Quadradinhos na gravura (agente consertando). Depois, juntos: a diferença de corte entre a prévia e o PDF, a faixa escura do Marial 7 e as sobras do Graduale.
2. **1.1 Tirar o fundo de PDF com camadas (começou em 28/09).** Primeiro só o núcleo (`core/camadas.py`): reconhecer sozinho o PDF do Internet Archive e montar a página com papel branco, letra na cor original e gravura/foto intactas. Depois: ligar ao processamento e pôr o botão de ligar e desligar (regra 8).
3. **1.3 Comparar os OCRs, só para achar onde está o texto.** Tesseract (com e sem o filtro do Internet Archive; modelos da UB Mannheim), docTR (OnnxTR) e PP-OCRv5 (RapidOCR); as linhas que já vêm nos PDFs do Internet Archive entram como referência. Medidas: quanto da tinta de texto cai nas caixas (meta: 98% ou mais) e quanto da tinta de gravura, iluminura, moldura e foto cai nelas (meta: 1% ou menos). Ficam os 2 melhores. **Precisa instalar programas (ver abaixo).**
4. **1.2 Seletor de gravura do ScanTailor, com o código original.** Recomendação da pesquisa: compilar só o detector numa biblioteca pequena (DLL), chamada pelo programa. A régua já existe: as máscaras que o próprio ScanTailor gravou no teste de 24/09. **Precisa de ferramentas de compilação (ver abaixo).**
5. **1.4 Máscara de tinta com a cor original**, só dentro das linhas de texto (usa o resultado do 1.3).
6. **1.5 Juntar os dois detectores e montar a página**, com as regras do resultado de 28/09: papel todo branco (inclusive dentro da gravura), iluminura e moldura intactas, a **moldura detectada como gravura** e o **botão de manter ou tirar a moldura**.
7. **1.6 PDF de saída em duas camadas**, como opção.

Cada item: implementador → verificador (antes/depois nas páginas do gabarito, sempre com as páginas obrigatórias e o aviso de defeito conhecido) → relatório → commit no `fase-1`. Item que mexe no processamento também passa pelo teste de velocidade.

## Preciso do Samuel: instalar programas

Neste PC não há compilador de C++, CMake, Tesseract nem Linux no WSL (conferido em 28/09).

- **Para o 1.3, Tesseract 5.5 (UB Mannheim).** Pede administrador. Os outros OCRs eu instalo sem administrador, num ambiente de teste separado, sem mexer no programa.
- **Kraken:** só roda em Linux (WSL com Ubuntu, 1 a 2 GB). **Recomendação:** deixar fora da primeira comparação e só instalar se os outros falharem, porque ele também exigiria o WSL no notebook do Kaique.
- **Para o 1.2, Visual Studio 2022 Build Tools (C++) e CMake.** Pede administrador; de 6 a 8 GB. O Qt de desenvolvimento eu baixo sem administrador.
- **Como instalar:** eu rodo os comandos e o Samuel só clica em "Sim" no aviso do Windows; ou ele mesmo roda:
  - `winget install --id UB-Mannheim.TesseractOCR`
  - `winget install --id Kitware.CMake`
  - `winget install --id Microsoft.VisualStudio.2022.BuildTools --override "--quiet --wait --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"`

## Uma correção num documento do Samuel

A pesquisa do 1.1 corrigiu duas frases do `TESTE-SCANTAILOR-MISTO.md`: (1) no Palatino, nenhuma página do gabarito tem "tudo na camada de baixo"; o fundo em resolução cheia das primeiras páginas é uma opção de qualidade do Internet Archive; (2) o Internet Archive também sobe moldura, gravura e pontinhos de foto para a camada de cima. O documento é do Samuel: ele decide se atualiza.

## Documentos da pesquisa

- `docs/pesquisa/fase1-1.1-camadas-internet-archive.md`
- `docs/pesquisa/fase1-1.2-scantailor.md`
- `docs/pesquisa/fase1-1.3-ocr-para-achar-texto.md`
