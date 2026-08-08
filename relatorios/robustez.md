# Robustez: o que acontece quando da errado

Cada linha e uma coisa que pode acontecer na mao do Kaique. O que se
cobra e sempre o mesmo: o programa nao pode fechar, a mensagem tem de
ser compreensivel por quem nao e tecnico, e o trabalho ja feito nao
pode se perder.

**20 de 20 casos passaram.**

| Situacao | O que e | Continuou de pe? | Mensagem | Perdeu trabalho? |
|---|---|---|---|---|
| OK PDF corrompido | arquivo picado no meio | sim | - | nao |
| OK Arquivo que nao e PDF | texto renomeado para .pdf | sim | Não consegui abrir esse arquivo. Ele pode estar danificado ou não ser um PDF. | nao |
| OK Arquivo vazio | zero byte | sim | Não consegui abrir esse arquivo. Ele pode estar danificado ou não ser um PDF. | nao |
| OK PDF protegido por senha | aberto so com senha | sim | Esse PDF está protegido por senha. Não consigo abrir. | nao |
| OK PDF de uma pagina so | livro minimo | sim | - | nao |
| OK PDF sem imagem | so texto vetorial | sim | - | nao |
| OK Paginas de tamanhos diferentes | no mesmo arquivo | sim | - | nao |
| OK Paginas giradas | 0, 90, 180 e 270 graus | sim | - | nao |
| OK Pagina gigante | tipo mapa dobrado, 3400x2200 pt | sim | - | nao |
| OK Pagina toda preta | scan falhado | sim | - | nao |
| OK Pagina toda branca | folha de guarda | sim | - | nao |
| OK Nome com acento e parenteses | 'Diario do Paroco (copia 2)' | sim | - | nao |
| OK Caminho com mais de 260 letras | pastas encadeadas | sim | - | nao |
| OK PDF de mais de 1000 paginas | 1010 paginas | sim | 1010 folhas analisadas em 12s | nao |
| OK Arquivo aberto em outro programa | travado por outro | sim | leitura funciona com o arquivo aberto por outro | nao |
| OK Arquivo some no meio (pendrive) | removido apos abrir | sim | Não consegui achar esse arquivo. Ele pode ter sido movido ou apagado. | nao |
| OK Disco cheio ou sem destino | unidade inexistente | sim | Não consegui gravar nessa pasta. Ela pode ter sido removida, estar cheia ou ser um pendrive que foi tirado. Escolha outra pasta e tente de novo. | nao |
| OK Cancelar no meio | usuario desiste | sim | nada pela metade ficou no disco | nao |
| OK Abrir varios livros sem reiniciar | um apos o outro | sim | tres livros seguidos, sem reiniciar | nao |
| OK Memoria com livro grande | 1 pagina contra 1010 | sim | 1 pagina: +5 MB; 1010 paginas: +4 MB | nao |
