# Etapa 5: teste da instalação e da atualização no PC do Samuel (relatório)

## 17/11/2026: começo da etapa 5 parado antes de qualquer passo

**O que aconteceu.** Antes de mexer no Windows, a lista manda ler no código onde a atualização guarda as versões que
baixa. Esse lugar é **dentro da pasta dos seus projetos**. A ordem da gerente para esse caso era parar e avisar.
Por isso nada foi feito no Windows: nenhuma foto nova, nenhuma cópia de reserva, nenhuma versão de mentira.

**O que está errado, em palavras simples.** O programa instalado fica em Arquivos de Programas. Quando o Kaique abre o
programa, a peça de atualização (Velopack) tenta gravar ali e não consegue, porque a conta dele abre o programa sem
licença de administrador. Ela então muda sozinha para um lugar de reserva:
`%LOCALAPPDATA%\EditorImpressao\packages`, com uma cópia do `Update.exe` em `%LOCALAPPDATA%\EditorImpressao\`.
Esse é o mesmo lugar dos projetos e das configurações do Kaique (e dos seus).

- **É defeito do programa**, não escolha sua. Ninguém pediu isso.
- **Quando acontece:** toda vez que a janela do programa instalado abre e olha a versão (a olhada do aviso de versão
  nova). A pasta é criada nessa hora.
- **Por que a troca de pasta do teste não protege:** o Velopack pergunta ao Windows onde fica essa pasta, sem ler a
  variável que o teste troca. No teste, a pasta iria para a sua pasta de projetos de verdade.
- **O que ainda não se sabe:** se desinstalar apaga essa pasta de reserva inteira. Não foi testado.

**De onde vem a prova (máquina, só lendo):**
- Código do Velopack (`locator.rs`, `known_path.rs`, ramo `develop`): sem gravação na pasta do programa, usa
  `LocalAppData` + id do pacote + `packages`, cria a pasta na hora e copia o `Update.exe`. O `LocalAppData` vem de
  `SHGetKnownFolderPath`.
- O Velopack do `.venv` (1.2.161) tem as mesmas frases dessa regra ("Using fallback directory", "Copied Update.exe
  from root to fallback", ".velopack_dir_test").
- O id do pacote é `EditorImpressao` (`versao.ID_DO_PACOTE`).
- No programa: `atualizacao.versao_que_roda` (chamada pelo aviso de versão nova, `ui/aviso_de_atualizacao.py`)
  cria o gerente do Velopack na conta do Kaique; o ajudante roda como o sistema e grava em `<programa>\packages`.

## O que foi feito

- Cópia nova do ramo final: `.claude\worktrees\etapa5`, ramo `etapa5-2026-11-17`, a partir de `a9d81030`.
- Os nomes de verdade (lista, A2), conferidos no código e escritos na `lista.md` e na `comandos.md`:
  - o ajudante: `EditorImpressao\Procurar versao nova`;
  - a tarefa "desfazer": `EditorImpressao\Desfazer testes a distancia`;
  - o "atualizar" de longe: `schtasks /Run /TN "EditorImpressao\Procurar versao nova"`;
  - a pasta de teste: o arquivo `C:\ProgramData\EditorImpressao\fonte-de-teste.txt`. Ele só vale se for dos
    Administradores ou do sistema. Isso foi conferido no código;
  - a versão que o programa mostra vem do Velopack. Uma pasta empacotada serve para todas as versões de mentira. O
    registro da atualização vai dizer "versão 1.1.0" no começo de toda linha.

## Fotos, cópia de reserva, versões de mentira

- **Fotos do Windows:** não tiradas (parado antes).
- **Cópia de reserva dos projetos:** não feita (parado antes).
- **Versões 1.1.0 a 1.1.5:** não feitas (parado antes).
- Nenhuma pergunta do Windows apareceu. Nada foi instalado, e nenhum arquivo foi criado no `ProgramData`.

## Outras coisas achadas (para a fase 1, quando ela voltar)

1. O publicar com uma pasta já pronta não põe o Visual C++ dentro do pacote e confere o pacote sem cobrá-lo. A 1.1.0
   tem de sair pelo caminho inteiro (com o Visual C++); as outras reaproveitam a pasta que ela deixa.
2. Numa cópia do projeto (worktree), o empacotador procura o motor do Kraken e o Visual C++ baixado numa pasta que
   não existe ali (`.claude\worktrees\EditorImpressao-arquivos`). É preciso apontar para
   `D:\programas\EditorImpressao-arquivos\ferramentas\` e ligar a pasta `modelos` por junção.
3. Sobra de outro agente, que já estava lá e não foi apagada: `%LOCALAPPDATA%\velopack\velopack_EditorImpressaoEnsaio.log`.

## Situação

NÃO ESTÁ PRONTO PARA SEGUIR. A gerente decide com o Samuel o que fazer com a pasta de reserva do Velopack, antes da
fase 0.
