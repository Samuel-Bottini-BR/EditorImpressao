"""Grava o relatorio do item 2.1 (dividir) nos tres formatos (relatorio.gravar)."""

from __future__ import annotations

import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parents[1]
RAIZ = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RAIZ))

import relatorio  # noqa: E402

TEXTO = r"""
# Item 2.1, dividir a folha: o do programa × o do ScanTailor

**06/10/2026 · implementador (ramo `fase2-dividir`) · PRONTO PARA CONFERIR é com o verificador; quem decide é o Samuel.**

Decisões do Samuel que este item cumpre (conferências 9 e 14, 05/10):
**G2 (a)** *"Só quando o Kaique pedir, livro a livro, escolhendo 'o do programa' ou 'o do ScanTailor', e trocando numa folha se um ficar ruim."*
**G3 (b)** o "corte da sobra" do ScanTailor como opção, desligada.
E a regra: *"o programa vai ter que ser capaz de abrir arquivos de versões anteriores."*

## Em poucas frases

1. **Livro novo não divide mais sozinho.** A caixinha "Dividir folhas ao meio" vem desmarcada. Marcada, aparece a escolha "Jeito de dividir: o do programa / o do ScanTailor".
2. **O do ScanTailor é o código original dele**, dentro da DLL comum, sem mudar uma letra (50 arquivos trazidos, cada um conferido pela soma). O limpar pontinhos e o detector de gravura continuam dando exatamente o mesmo resultado.
3. **Numa folha só dá para trocar o jeito** (aba Onde cortar, lista "jeito:"), e o "não dividir esta" agora funciona: antes ele fazia o PDF sair com a folha **repetida** (era um defeito escondido; consertado junto).
4. **Projeto antigo abre como estava:** o que estava dividido continua dividido, pelo jeito do programa. Conferido em 28 páginas: prévia e PDF idênticos, ponto a ponto, ao programa de antes.
5. **Nos testes, os dois jeitos erram em lugares diferentes** (como no D3): no livro aberto de verdade os dois acertam a dobra, e o do ScanTailor fica mais no meio dela; no Siebmacher (uma página deitada) os dois partem a folha; o do ScanTailor parte a tabela do Opus Majus 256. **O corte da sobra continua comendo letra** na Escola 7 e 35 e levando o "Cvij" do Graduale 221. Ele está desligado de fábrica, como decidido.
6. **Tempo:** quem não usa o ScanTailor não perde nada. Com o do ScanTailor, abrir o livro fica mais lento (Hugon, 471 folhas: 46 s → 76 s). Com o corte da sobra, também (Escola, 199 folhas: 17 s → 39 s).

## Como ler as imagens

Em cima, **cada jeito numa cópia** do original, com a linha dele (nunca por cima do resultado). Embaixo, **as páginas que saem**, lado a lado (sem cortar as bordas nem endireitar, para só a divisão aparecer). As cores:

- **A. o do programa** (azul): o livro marcado para dividir, pelo jeito do programa;
- **B. o do ScanTailor** (vermelho): o livro marcado, pelo jeito do ScanTailor;
- **C. ScanTailor + corte da sobra** (laranja): B, com "Cortar a beirada da folha vizinha" marcada (linhas tracejadas = o que fica);
- **D. não dividir + corte da sobra** (verde): o livro sem dividir, só com o corte da sobra.

Tudo passou pelo programa como ele abre o livro (a folha a 150 DPI). Nas folhas de livro aberto há também a **dobra ampliada**.

## Páginas-gabarito

### Siebmacher 7 e 9 (uma página só, deitada)

![Siebmacher 7](imagens/siebmacher_p007.jpg)

![Siebmacher 9](imagens/siebmacher_p009.jpg)

- **O do programa** divide a 57%, no meio do poema e da moldura (igual ao D3).
- **O do ScanTailor** divide a 74%, **em cima da moldura da direita**: a página da direita fica com uma tira da moldura. (No D3 ele dividiu a 80-82%, na beirada do livro; a diferença é a resolução: a 300 DPI ele acha 80-82%, a 100-200 DPI acha 74%. O programa analisa a 150 DPI.)
- **D (não dividir + sobra)**: uma página inteira, certa, nada cortado.
- **Opinião:** neste livro o certo é **não dividir**. Os dois jeitos erram; é o caso da escolha "não", que agora é a de fábrica.

### Opus Majus 256 (tabela numa folha dobrável deitada)

![Opus 256](imagens/opusmajus_p256.jpg)

- **O do programa** não divide (a folha é só um pouco mais larga que alta; o do programa só divide a partir de 1,2 vez). **Certo.**
- **O do ScanTailor** divide a 50%, **no meio da tabela** (ele divide toda folha mais larga que alta).
- **Opinião:** se este livro for marcado "o do ScanTailor", esta folha tem de ser trocada na aba Onde cortar ("não dividir esta").

### Na escola de Jesus 7 e 35, Graduale 221 e 222 (uma página em pé; o corte da sobra)

![Escola 7](imagens/escola_p007.jpg)

![Escola 35](imagens/escola_p035.jpg)

![Graduale 221](imagens/graduale_p221.jpg)

![Graduale 222](imagens/graduale_p222.jpg)

- **Nenhum dos dois divide** estas folhas (certo).
- **O corte da sobra** (C e D, iguais aqui): na **Escola 7** a linha da direita (94%) passa rente ao fim das linhas e lasca a última letra; na **Escola 35** corta **o começo e o fim das linhas** dos dois lados (10% e 87%); no **Graduale 221** leva o **"Cvij"** e os ganchinhos do fim das pautas (90%); no **Graduale 222** o corte da esquerda (22%) fica **rente às claves**.
- **Opinião:** é o mesmo defeito do D3. O corte da sobra **não deve ser ligado** nestes livros; está certo ele vir desligado.

### Livro de Horas 11 e Palatino 5 (controle)

![Horas 11](imagens/horas_p011.jpg)

![Palatino 5](imagens/palatino_p005.jpg)

- Ninguém divide. Na Horas 11 o corte da sobra tira só a beirada (2% e 98%), sem tocar na iluminura. No Palatino 5 o ScanTailor não vê sobra nenhuma.

## Livro escaneado aberto (duas páginas por foto)

Do acervo (somente leitura): **Tractatus Dogmatici, vol. 3 (Hugon)**, 471 folhas, fotografado com a dobra escura no meio; e **O Corpo Místico (Penido)**, cópia xerox.

![Hugon 1](imagens/hugon_f001.jpg)

![Hugon 1, dobra](imagens/hugon_f001_dobra.jpg)

![Hugon 41](imagens/hugon_f041.jpg)

![Hugon 41, dobra](imagens/hugon_f041_dobra.jpg)

![Hugon 121](imagens/hugon_f121.jpg)

![Hugon 121, dobra](imagens/hugon_f121_dobra.jpg)

![Hugon 241](imagens/hugon_f241.jpg)

![Hugon 241, dobra](imagens/hugon_f241_dobra.jpg)

![Hugon 361](imagens/hugon_f361.jpg)

![Hugon 361, dobra](imagens/hugon_f361_dobra.jpg)

![Hugon 471](imagens/hugon_f471.jpg)

![Hugon 471, dobra](imagens/hugon_f471_dobra.jpg)

![Penido 3](imagens/penido_f003.jpg)

![Penido 3, dobra](imagens/penido_f003_dobra.jpg)

![Penido 91](imagens/penido_f091.jpg)

![Penido 91, dobra](imagens/penido_f091_dobra.jpg)

- **Hugon:** os dois dividem toda folha, **sem cortar letra**. O **do programa** corta sempre a 46%, **na borda esquerda da sombra da dobra**: a página da direita leva a sombra inteira. O **do ScanTailor** corta entre 47% e 53%, **na própria dobra** (na linha escura) nas folhas 1, 41, 361 e 471, e logo à direita da sombra nas 121 e 241.
- **Penido:** os dois acertam o espaço branco entre as páginas (programa 53-55%, ScanTailor 51-52%), sem tocar no texto.
- **D (não dividir + sobra):** nada é cortado (o automático do ScanTailor vê duas páginas e não corta sobra).
- **Opinião:** no livro aberto de verdade, **o do ScanTailor divide mais no meio da dobra**; o do programa é seguro, mas deixa a sombra toda de um lado. Nos dois, a sombra que sobra sai depois, no "cortar as bordas".

## Uma escolha minha, para a gerente levar ao Samuel

O ScanTailor tem dois jeitos de achar a sobra: o **automático** (o que ele faz sozinho, e o que o Samuel viu no D3) e o modo **"uma página + sobra" forçado** (o botão dele). Testei os dois. O forçado, **numa folha de livro aberto, tomou a dobra do meio por beirada e jogou fora uma página inteira** (Hugon 121: ficou de 0% a 54%), e na tabela do Opus 256 cortou colunas (ficou de 22% a 84%). Por isso o programa usa o **automático**. O custo: na folha deitada de uma página (Siebmacher) o automático não corta sobra nenhuma (o forçado tirava só a beirada, bem). As imagens do forçado estão em `imagens/sobra-modo-forcado/` e os números em `dados/medidas-sobra-modo-forcado.json`.

## O que entrou

- **DLL comum `st_ferramentas`** (versão da interface 2): função nova `st_ferramentas_dividir`, a mesma chamada que o ScanTailor faz (`PageLayoutEstimator::estimatePageLayout`). Os pontinhos não mudaram.
- **50 arquivos do ScanTailor v1.2.1** (commit `5eaac18`) em `terceiros/scantailor-advanced/src`, **sem mudança**, com a soma em `somas-v1.2.1.txt` (conferida três vezes contra o git do ScanTailor). A única função copiada como "cola" (`adviseNumberOfLogicalPages`, 10 linhas) está entre marcas e um teste confere que é igual ao original (`referencia/ProjectPages.cpp`).
- **Conferido com os arquivos novos:** limpar pontinhos igual ponto a ponto à DLL anterior (96 de 96 imagens); detector de gravura recompilado em rascunho dá as mesmas 64 máscaras; a DLL do 1.2 não foi tocada.
- **Projeto:** `dividir_folhas` (de fábrica agora desmarcado), `dividir_como` (programa / scantailor), `cortar_sobra` (desligado). **Folha:** `dividir_como` (vazio = segue o livro) e `sobra`.

## Como ficou na tela (aparência provisória, para o agente de layout)

Tela **"O que fazer"** (`ui/tela_opcoes.py`):

- caixinha **"Dividir folhas ao meio"** (já existia; agora vem desmarcada);
- logo abaixo, só com ela marcada: rótulo **"Jeito de dividir:"** + lista com **"o do programa"** e **"o do ScanTailor"**;
- caixinha nova **"Cortar a beirada da folha vizinha"**, com a explicação "o corte da sobra do ScanTailor, nas folhas que não forem divididas" (desmarcada de fábrica);
- o resumo embaixo diz o jeito: "dividir as N folhas em 2N páginas (jeito: o do ScanTailor)" e "cortar a beirada da folha vizinha (o corte da sobra do ScanTailor)".

Aba **"Onde cortar"** (`ui/tela_conferir.py`), na linha de botões:

- rótulo **"jeito:"** + lista **"o do programa" / "o do ScanTailor"**: troca o jeito só desta folha e a linha azul vai para onde o outro jeito acha (uma ação do desfazer; ~0,1 s). Apagada em folha não dividida;
- botão **"não dividir esta" / "dividir esta"** (já existia): agora apaga (ou devolve) a metade da direita na mesma ação. Em folha que entrou como uma página só ele fica apagado, com a dica "Esta folha entrou como uma página só. Para dividir, volte e marque 'Dividir folhas ao meio' no livro."

## Testes de máquina

- `pytest tests`: **1825 passaram, 0 falharam** (59 pulados, como antes). Novos: `test_dividir_scantailor.py` (DLL, cópia fiel, gabarito do D3), `test_dividir_no_programa.py` (modelo, projeto antigo, análise, sobra, zonas, "não dividir esta", trabalho salvo) e `test_dividir_na_tela.py` (as duas telas, desfazer).
- `teste_botoes.py` numa cópia (`git archive`), com `saida_teste` própria: **166 ações, 0 falhas**, agora passando também pela aba Onde cortar e pelas escolhas novas.
- **Projeto antigo** (`scripts/projeto_antigo.py`): 16 páginas do Hugon e 12 do Siebmacher, gravadas sem os campos novos e abertas pelo programa de antes e pelo de agora: **divisão, prévias e PDF idênticos** (`dados/antigo_*.json`).

## Tempo (pasta de dados de rascunho; duas rodadas, a média)

| Livro | Programa de antes | Agora, sem dividir | Agora, o do programa | Agora, o do ScanTailor | Agora, ScanTailor + sobra |
|---|---|---|---|---|---|
| Hugon, 471 folhas, abrir | 46,3 s | 43,7 s | 46,1 s | 76,1 s | 76,5 s |
| Hugon, processar 10 páginas | 5,0 s | (10 folhas inteiras) | 4,9 s | 5,2 s | 5,3 s |
| Escola, 199 folhas, abrir | 17,6 s | 17,0 s | 16,9 s | — | 39,1 s |
| Escola, processar 10 páginas | 5,1 s | 4,9 s | 5,0 s | — | 4,6 s |

Quem não marca o ScanTailor não perde tempo (regra 6). O do ScanTailor custa uns 65 milésimos por folha ao abrir; o corte da sobra, uns 110. Trocar o jeito de uma folha na aba Onde cortar: 0,1 s.

## Ressalvas

- **A linha do ScanTailor pode ser inclinada**; o nosso corte é reto: fica o meio da linha (na sobra, a ponta que corta menos). Nas folhas testadas a inclinação foi de no máximo 5% da largura (Escola 35, na sobra).
- **O ScanTailor muda de ideia com a resolução** (Siebmacher: 74% a 150 DPI, 80-82% a 300 DPI). O programa usa a folha da análise, a 150 DPI.
- **Folha girada perde o corte da sobra** (a sobra é medida na folha como veio).
- **"Dividir esta" numa folha que entrou como uma página só não existe** (a lista de páginas não muda durante a conferência; quem divide é o livro). Na sugestão do alerta "Esta folha parece ter uma página só", o botão "não dividir esta" agora só marca a folha como conferida.
- **Mudar o jeito do livro depois de conferir:** se as mesmas folhas continuam divididas, o trabalho volta e as folhas que seguem o livro ganham a divisão nova; se outras folhas passam a ser divididas, a conferência recomeça (com cópia do trabalho), como já acontecia ao mudar "Dividir folhas ao meio".
- O jeito de fábrica, quando a pessoa marca "Dividir", é **"o do programa"** (o que o programa já fazia). O Samuel não disse qual; é uma pergunta.
- Testes que partiam de "livro novo divide" foram ajustados para marcar a divisão; achado junto: sem dividir, dois testes que comparam o arquivo do projeto ficavam instáveis (a prévia grava por trás). Medido no programa de antes com o de fábrica trocado: 2 falhas em 5 rodadas.

## Para a Lista de bugs

- 06/10, aba Onde cortar: o alerta "Esta folha parece ter uma página só. Confirme se devo dividir." oferece o botão laranja "não dividir esta" numa folha que já não é dividida (texto trocado; agora ele só marca como conferida).

## Ideias para a Lista de espera

- Calcular o do ScanTailor por trás, depois que o livro abre, para o "abrir" não ficar mais lento.
- Uma lista "corte da sobra: automático / forçado" (o forçado é bom na folha deitada de uma página, ruim no livro aberto).

## Arquivos

Imagens em `imagens/`; números em `dados/` (`medidas.json`, `tempos/`, `antigo_*.json`); scripts em `scripts/` (`lado_a_lado.py`, `tempo.py`, `projeto_antigo.py`, `gravar_relatorio.py`).
"""


def main() -> int:
    feitos = relatorio.gravar(TEXTO.strip() + "\n", PASTA / "relatorio",
                              titulo="Item 2.1 - dividir a folha")
    for tipo, caminho in feitos.items():
        print(tipo, caminho)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
