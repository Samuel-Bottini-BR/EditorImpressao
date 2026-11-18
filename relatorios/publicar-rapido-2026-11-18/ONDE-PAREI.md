# ONDE PAREI — estudo "publicar rápido" (pesquisador, 18/11/2026)

Ramo `publicar-rapido-2026-11-18` (a partir de `obra-2026-10-26`, `01c4576f`), cópia
`.claude/worktrees/publicar-rapido`. Pasta de trabalho: `saida_teste/publicar-rapido/`.
Só estudo e medida: nenhuma linha do programa, dos scripts de publicar ou dos testes muda (D-765).

## Decisões que esta tarefa precisa cumprir

- **D-765** (17/11): "eu não quero fazer nenhum conserto até o .exe estar pronto para o kaique e a questão de eu poder lançar testes no pc dele funcionar." → nada no programa muda; só relatório.
- **D-766** (17/11): "os proximos consertos eu quero poder arrumar e poder atualizar a versão dele sempre que eu puder" → é por isso que publicar precisa ser rápido.
- **D-714** (16/11): versão publicada de propósito ("1 - vamos seguir sua sugestão").
- **D-723** (16/11): "velopack" → a ferramenta continua o Velopack.
- **D-724** (16/11): "gratis, mas o que é essa assinatura e é segura?" → toda saída tem de manter a assinatura do PC do Samuel conferida antes de instalar.
- **D-727** (16/11): "se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador né" → nada baixado na hora de instalar.
- **D-713** (16/11): "não precisa ser privado" → as versões vêm do GitHub público.
- **D-736** (17/11): "Se tiver nova versão eu quero poder mandar atualizar aqui pelo meu pc" → a versão publicada tem de servir também ao comando de longe.
- **D-763/D-764** (17/11): nome interno `EditorImpressaoPrograma`; o desinstalador do .msi 1.2.161 foi o provado ("SUBIR DE VERSAO EXIGE REPETIR A PROVA", empacotar.py).
- **D-730** (16/11): o instalador antigo fica de reserva até a etapa 5 passar.
- **D-300** (18/07): "Instalador em português, com desinstalador e versão portátil."
- CLAUDE.md §6: trocar biblioteca (ex.: Velopack mais novo) precisa perguntar.
- CLAUDE.md §11.12 (sem gambiarra) e §11.13 (formato das perguntas).

## O que já está escolhido e testado aqui

- `empacotar.comando_do_vpk` (a regra única do comando do `vpk pack`): `--msi --instLocation PerMachine`, `--runtime win-x64`, `--icon`, sem `--framework`, sem `--delta` (vale o padrão BestSpeed). Testes: `tests/test_empacotar.py`, `tests/test_nome_do_pacote.py`, `tests/test_decisoes_atualizacao.py`.
- `publicar_versao_kaique.publicar`: chave → versão nova → `vpk download` → empacotar → assinar o pacote inteiro → `vpk upload`.
- Etapa 5 (preparada e em andamento com o Samuel): servidor de mentira `saida_teste/etapa5/servidor/` com 1.1.0 a 1.1.5. **Só leitura.**

## Como fica para quem usa e no livro

Nada muda no PDF nem nas telas: é só o jeito de montar e publicar a versão no PC do Samuel. Para o Kaique, o que
pode mudar (por opção) é só o tamanho do que ele baixa e qual instalador fica disponível para uma instalação nova.

## Andamento

- 07:14 começo; li pesquisador.md, CLAUDE.md inteiro, INDICE, ficha 6.8, decisões, linha do plano, os dois registros.
- Código do Velopack 1.2.161 (MIT) baixado em `saida_teste/publicar-rapido/fonte-velopack/repo` e lido: PackageBuilder,
  WindowsPackCommandRunner, DeltaPackageBuilder, EasyZip. Documentação (velopack.docs) em `.../docs/repo`.
- Medidas leves feitas (só leitura dos pacotes do servidor da etapa 5): divisão do pacote por pasta; conteúdo do delta.
- ~07:20 recado da gerente: etapa 5 começou; **nada de medida pesada sem o "pode" dela**. Parei a contagem que rodava.
- ~07:25 pedi à gerente o "pode" das medidas M1 a M5. Resposta: esperar a etapa 5 parar; deixar o relatório pronto com estimativas "[não medido]"; não entregar sem as medidas.
- 07:29 rascunho do relatório gravado em três formatos (relatorio.md/.html/.pdf), com os números a medir marcados.
- 10:40 dado novo da gerente (o lado do Kaique): lido o atualizacao.log da etapa 5 e o código do Velopack do lado do cliente. Achados: a troca pela diferença leva ~22-23 min (remonta o pacote inteiro), pelo pacote inteiro ~7,5 min; **a diferença não passa pela assinatura** (D-724), dedução da leitura, avisada à gerente. Relatório refeito (seção 2b, pergunta 3 nova: diferença ou versão inteira).
- 12:06 "pode" da gerente (etapa 5 terminada). Medidas M1, M2a, M2b, M3, M4, M5, M5b feitas até 13:32 (números na
  seção 8 do relatório). Achado novo: o vpk 1.2.161 recusa `--noInst` com `--noPortable`; a versão de atualização
  usa `--noPortable` sem `--msi`.
- 13:32 C: caiu para 9,9 GB livres por outra coisa (não a minha pasta). A trava do Claude Code não deixou apagar
  `C:\pr-medida` (pasta na raiz do C:); avisado à gerente, não contornado.
- Relatório final gravado nos três formatos; entrega à gerente.

## Como cumpri cada decisão

- D-765: nenhuma linha do programa, dos scripts de publicar ou dos testes mudou (`git status` da cópia: só
  `relatorios/`). As medidas usaram o vpk direto e um script meu fora do código
  (`saida_teste/publicar-rapido/medir/`). Na M5, rodei a função `empacotar.construir_pasta` sem mudar o código.
- D-766: o estudo mede o tempo de publicar e de atualizar, que é o que pesa em "atualizar sempre que eu puder".
- D-714, D-723, D-713: nenhuma saída troca o Velopack, a publicação de propósito ou o GitHub público.
- D-724: toda saída foi conferida contra a assinatura. Achado: pelo caminho da diferença ela não cobre o que é
  instalado (relatório, seção 2b), e isso virou a pergunta 3.
- D-727: nenhuma saída baixa algo na instalação. A 3.5 (motor fora do pacote) mexeria nisso, por isso fica para
  depois, com plano.
- D-736: a versão publicada serve igual ao comando de longe; nada muda.
- D-763/D-764: o nome interno não muda. O Velopack mais novo exigiria refazer a prova do desinstalar (seção 3.6).
- D-730: o instalador antigo não foi tocado.
- D-300: a versão portátil (a pasta) continua; o zip portátil do Velopack vai na pergunta 2.
- §6: nenhuma biblioteca trocada.
- §11.12: em cada saída está dito onde mora a regra e por quais caminhos (seção 3).
- §11.13: as perguntas estão no formato pedido (seção 5).
- Etapa 5: `saida_teste\etapa5` e a cópia `etapa5` foram só lidas (o `dist`, o servidor, os registros e o
  `atualizacao.log`).
- A chave do Samuel não foi lida nem tocada, e nenhuma medida assinou nada.
- Nenhuma janela foi aberta na tela do Samuel e nenhum outro agente foi aberto.

## Disco (o que ficou)

- **C:** `C:\pr-medida\` (~2,5 GB, só arquivos meus: `base-1.1.0-full.nupkg`, `delta-BestSpeed.nupkg`,
  `delta-m5.nupkg`, `saida-m5\` e `temp\`). **Precisa ser apagada por uma pessoa:** a trava de segurança do Claude
  Code recusou o `rm` de uma pasta na raiz do C:.
- **D:** `saida_teste\publicar-rapido\fonte-velopack\` (código e documentação do Velopack, ~0,5 GB, para consulta;
  pode ser apagada) e `saida_teste\publicar-rapido\medir\` (o script, o registro, as vigias, a diferença da M4 com
  ~20 MB e o `temp\`). A pasta do programa e o `build\` que a M5 montou na cópia do estudo foram apagados. A junção
  `modelos` da cópia foi removida só como junção, e o original `D:\programas\EditorImpressao\modelos` continua inteiro.
- A cópia `.claude\worktrees\publicar-rapido` (ramo `publicar-rapido-2026-11-18`) fica, com o relatório.

## Perguntas para o Samuel

(no relatório, seção 5, formato §11.13: 1. montar no C:; 2. instalador só quando pedir; 3. diferença ou versão inteira (e a assinatura); 4. motor do Kraken fora, para depois)

## Medidas planejadas (feitas em 18/11, 12:06 a 13:32; resultados no relatório, seção 8)

- M1: copiar a pasta do programa (só leitura do `dist` da etapa 5) para o C: (`C:\pr-medida\`) e para `saida_teste\publicar-rapido\`.
- M2: no C:, `vpk pack` sem instalador, sem portátil, sem diferença (TEMP no C:); medir o pico de espaço e o tempo de conferir+assinar.
- M3: no C:, `vpk delta generate` entre a 1.1.0 e a 1.1.1 do servidor (copiadas): BestSpeed e BestSize.
- M4: a mesma diferença no D:, sozinha.
- M5 (opcional): montar a pasta na minha cópia (PyInstaller) e medir a diferença com o código mudado de verdade.
- Limites: no máximo ~8 GB no C: (apagar no fim) e ~40 GB no D:.
