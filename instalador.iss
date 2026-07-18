; Instalador do Editor de Impressao (Inno Setup 6)
;
; Gere com:  python empacotar.py --modo instalador
; Sai em:    dist\EditorImpressao-Setup.exe
;
; O instalador empacota a versao EM PASTA (onedir), e nao o arquivo unico.
; Motivo: o arquivo unico se descompacta inteiro a cada abertura, o que custa
; uns 4 segundos a mais (~12 s contra ~8 s ate a janela aparecer). O arquivo
; unico continua existindo para quem quer levar no pendrive.

#define MeuNome "Editor de Impressao"
#define MeuExe "EditorImpressao.exe"
#define MeuAutor "Instituto de Preservacao de Livros"
#define MinhaVersao "1.0.0"

[Setup]
; NAO troque este AppId: e por ele que o Windows reconhece uma atualizacao
; como sendo o mesmo programa, em vez de instalar uma segunda copia.
AppId={{7C4E1B92-3A5D-4F18-9B6C-2E8A5D0F3C71}
AppName={#MeuNome}
AppVersion={#MinhaVersao}
AppVerName={#MeuNome} {#MinhaVersao}
AppPublisher={#MeuAutor}
VersionInfoVersion={#MinhaVersao}

; Instala em Arquivos de Programas
DefaultDirName={autopf}\{#MeuNome}
DefaultGroupName={#MeuNome}
DisableProgramGroupPage=yes
PrivilegesRequired=admin

; Aparece em "Adicionar ou remover programas"
UninstallDisplayName={#MeuNome}
UninstallDisplayIcon={app}\{#MeuExe}

OutputDir=dist
OutputBaseFilename=EditorImpressao-Setup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
ArchitecturesAllowed=x64compatible

; Frases da propria janela do instalador, em portugues
AppComments=Recupera livros escaneados e prepara para reimpressao
AppReadmeFile={app}\LEIAME.md

[Languages]
Name: "brasileiro"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[CustomMessages]
brasileiro.CriarAtalhoAreaTrabalho=Criar um atalho na Area de Trabalho
brasileiro.AtalhosAdicionais=Atalhos adicionais:
brasileiro.AbrirPrograma=Abrir o {#MeuNome}

[Tasks]
Name: "atalhoareatrabalho"; Description: "{cm:CriarAtalhoAreaTrabalho}"; \
    GroupDescription: "{cm:AtalhosAdicionais}"

[Files]
; Tudo que o PyInstaller gerou em modo pasta
Source: "dist\EditorImpressao\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "LEIAME.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Menu Iniciar
Name: "{autoprograms}\{#MeuNome}"; Filename: "{app}\{#MeuExe}"
; Area de trabalho (so se o usuario marcar)
Name: "{autodesktop}\{#MeuNome}"; Filename: "{app}\{#MeuExe}"; Tasks: atalhoareatrabalho

[Run]
; Oferece abrir o programa ao terminar
Filename: "{app}\{#MeuExe}"; Description: "{cm:AbrirPrograma}"; \
    Flags: nowait postinstall skipifsilent

[UninstallDelete]
; A pasta de trabalho do proprio programa fica em %LOCALAPPDATA% e NAO e
; apagada de proposito: ali estao o historico e os projetos do usuario.
; Aqui limpamos so o que o instalador criou.
Type: filesandordirs; Name: "{app}\_internal"
