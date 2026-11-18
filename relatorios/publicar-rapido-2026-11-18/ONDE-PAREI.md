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
- Próximo: relatório com o que se sabe do código e dos registros; plano de medidas pesadas para pedir o "pode".

## Perguntas para o Samuel

(no relatório, formato §11.13)
