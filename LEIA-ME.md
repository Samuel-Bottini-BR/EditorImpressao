# Ramo `prints-testes`: os prints da janela real tirados no Windows do GitHub

Este ramo **não é o programa**. Guarda só as imagens que o job "Botoes e prints
da janela real" (`.github/workflows/testes-windows.yml`, no ramo do programa)
tira a cada rodada dos testes no Windows do GitHub, para quem não consegue
baixar os "artifacts" do GitHub poder ver os prints pelo git.

- Cada rodada fica numa pasta `AAAA-MM-DD_HHMM_<commit>/`: a data e a hora em
  que o job gravou (hora de Greenwich, UTC; em Brasília são 3 horas a menos) e
  os 7 primeiros caracteres do commit do programa que foi testado.
- Dentro, cada momento sai em dois prints: `-janela.png` (o que o programa
  desenhou) e `-tela-inteira.png` (a tela do Windows inteira, com a barra de
  título). Os números do começo do nome dizem a ordem (tela inicial nos temas
  escuro, cinza e claro; "O que fazer"; conferir). `aviso-N.png`, se houver, é
  uma caixa de aviso que apareceu e foi respondida sozinha.
- Quem escreve aqui é só o workflow. Autorizado pelo Samuel em 09/10/2026.
- **Apagar este ramo não afeta o programa** nem os testes; só some o
  histórico de prints. As pastas antigas podem ser apagadas à vontade.
