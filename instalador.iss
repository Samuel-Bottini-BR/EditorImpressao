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

; OS MODELOS (redes neurais) VAO DENTRO DE dist\EditorImpressao\_internal\,
; postos la pelo empacotar.py (modelos_do_programa), e entram no instalador
; pela linha "dist\EditorImpressao\*" da secao [Files]. Eles ficam fora do
; git, e ate 28/09/2026 nunca entravam: o programa instalado rodava sem o
; detector de gravura e letra e sem a selecao por clique, sem avisar (Lista
; de bugs, 25/09). Por isso este script SE RECUSA a compilar (#error) se
; algum faltar - vale tambem para quem compilar este .iss na mao, sem passar
; pelo empacotar.py. Se o codigo (core/detectar_regioes.py,
; core/rede_selecao.py) mudar o nome ou o lugar de um modelo, mude aqui
; tambem (o teste tests/test_empacotar.py confere que as duas listas batem).
#define PastaDoPrograma AddBackslash(SourcePath) + "dist\EditorImpressao\"
#if !FileExists(PastaDoPrograma + "_internal\modelos\doclayout.onnx")
  #error Falta _internal\modelos\doclayout.onnx (detector de gravura e letra). Gere o instalador pelo empacotar.py.
#endif
#if !FileExists(PastaDoPrograma + "_internal\modelos\mobile_sam\mobile_sam.encoder.onnx")
  #error Falta _internal\modelos\mobile_sam\mobile_sam.encoder.onnx (selecao por clique). Gere o instalador pelo empacotar.py.
#endif
#if !FileExists(PastaDoPrograma + "_internal\modelos\mobile_sam\sam_vit_h_4b8939.decoder.onnx")
  #error Falta _internal\modelos\mobile_sam\sam_vit_h_4b8939.decoder.onnx (selecao por clique). Gere o instalador pelo empacotar.py.
#endif
#if !FileExists(PastaDoPrograma + "_internal\modelos\doctr\rep_fast_base-1b89ebf9.onnx")
  #error Falta _internal\modelos\doctr\rep_fast_base-1b89ebf9.onnx (detector de texto docTR). Gere o instalador pelo empacotar.py.
#endif

; O DETECTOR DE GRAVURA DO SCANTAILOR (item 1.2, 29/09/2026): a DLL
; core\nativo\st_gravura.dll (codigo original do ScanTailor Advanced, GPL-3)
; e o st_gravura.txt que diz de onde ela veio, postos pelo empacotar.py
; (nativos_do_programa) em _internal\core\nativo\. Mesma trava dos modelos:
; sem ela o programa cairia no detector de gravura antigo sem avisar.
#if !FileExists(PastaDoPrograma + "_internal\core\nativo\st_gravura.dll")
  #error Falta _internal\core\nativo\st_gravura.dll (detector de gravura do ScanTailor). Gere o instalador pelo empacotar.py.
#endif
#if !FileExists(PastaDoPrograma + "_internal\core\nativo\st_gravura.txt")
  #error Falta _internal\core\nativo\st_gravura.txt (origem e licenca do detector de gravura). Gere o instalador pelo empacotar.py.
#endif

; OS DETECTORES DE TEXTO (item 1.3, 29/09/2026: "todos os OCRs instalados").
; O empacotar.py poe ao lado do .exe o motor do Kraken (motor-kraken\) e o
; Tesseract com os seis idiomas (tesseract\), e deixa o instalador oficial do
; Visual C++ em build\vc_redist.x64.exe (conferido pela assinatura digital da
; Microsoft). Mesma trava dos modelos: faltando qualquer peca, nao compila.
#if !FileExists(PastaDoPrograma + "motor-kraken\python\python.exe")
  #error Falta motor-kraken\python\python.exe (motor do Kraken). Gere o instalador pelo empacotar.py.
#endif
#if !FileExists(PastaDoPrograma + "motor-kraken\servidor_kraken.py")
  #error Falta motor-kraken\servidor_kraken.py (motor do Kraken). Gere o instalador pelo empacotar.py.
#endif
#if !FileExists(PastaDoPrograma + "motor-kraken\python\Lib\site-packages\kraken\blla.mlmodel")
  #error Falta o modelo do Kraken (motor-kraken\...\kraken\blla.mlmodel). Gere o instalador pelo empacotar.py.
#endif
#if FileExists(PastaDoPrograma + "motor-kraken\python\msvcp140.dll")
  #error O motor do Kraken e do jeito velho (Visual C++ dentro dele). Monte um novo com montar_motor_kraken.py.
#endif
#if !FileExists(PastaDoPrograma + "tesseract\tesseract.exe")
  #error Falta tesseract\tesseract.exe. Gere o instalador pelo empacotar.py.
#endif
#if !FileExists(PastaDoPrograma + "tesseract\LICENSE")
  #error Falta tesseract\LICENSE (licenca do Tesseract). Gere o instalador pelo empacotar.py.
#endif
#define Idioma(Nome) \
  FileExists(PastaDoPrograma + "tesseract\tessdata\" + Nome + ".traineddata") ? "" : Nome + " "
#define IdiomasFaltando Idioma("lat") + Idioma("ita") + Idioma("por") + Idioma("fra") + Idioma("eng") + Idioma("script\Fraktur")
#if IdiomasFaltando != ""
  #error Faltam idiomas do Tesseract em tesseract\tessdata: {#IdiomasFaltando}. Gere o instalador pelo empacotar.py.
#endif
#define VcRedist AddBackslash(SourcePath) + "build\vc_redist.x64.exe"
#if !FileExists(VcRedist)
  #error Falta build\vc_redist.x64.exe (Visual C++ oficial da Microsoft). Gere o instalador pelo empacotar.py.
#endif
; A versao do Visual C++ que vai no instalador, lida do proprio arquivo
; (ex.: 14.44.35211.0 -> VcMaior 14, VcMenor 44, VcBuild 35211).
#define VcMaior 0
#define VcMenor 0
#define VcBuild 0
#define VcRev 0
#expr ParseVersion(VcRedist, VcMaior, VcMenor, VcBuild, VcRev)
#if VcMaior != 14
  #error build\vc_redist.x64.exe nao parece o Visual C++ 2015-2022 (versao {#VcMaior}).
#endif

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
brasileiro.CriarAtalhoAreaTrabalho=Criar um atalho na Área de Trabalho
brasileiro.AtalhosAdicionais=Atalhos adicionais:
brasileiro.AbrirPrograma=Abrir o {#MeuNome}

[Tasks]
Name: "atalhoareatrabalho"; Description: "{cm:CriarAtalhoAreaTrabalho}"; \
    GroupDescription: "{cm:AtalhosAdicionais}"

[Files]
; Tudo que o PyInstaller gerou em modo pasta, inclusive os modelos em
; _internal\modelos\ (ver a conferencia la em cima)
; Tambem o motor do Kraken (motor-kraken\) e o Tesseract (tesseract\), que o
; empacotar.py pos ao lado do .exe.
Source: "dist\EditorImpressao\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "LEIAME.md"; DestDir: "{app}"; Flags: ignoreversion
; O instalador oficial do Visual C++ (Microsoft). Nao vai para {app}: e tirado
; para uma pasta temporaria e rodado so se precisar (ver [Code]).
Source: "build\vc_redist.x64.exe"; Flags: dontcopy

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
Type: filesandordirs; Name: "{app}\motor-kraken"
Type: filesandordirs; Name: "{app}\tesseract"

[Code]
{ O VISUAL C++ DO MOTOR DO KRAKEN (decisao do Samuel, 29/09/2026: "O
  instalador roda o instalador oficial da Microsoft, e pula se ja estiver
  instalado").

  Como se sabe se esta instalado: pela chave de registro que a propria
  Microsoft documenta para o Visual C++ 2015-2022 x64,
    HKLM\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64
  (valores Installed, Major, Minor, Bld). O vc_redist e um programa de 32
  bits e costuma gravar na vista de 32 bits do registro (WOW6432Node); por
  isso as duas vistas sao lidas e vale a versao MAIOR. No PC do Samuel, em
  29/09, as duas existiam, com 14.44 e 14.50.

  Roda o vc_redist se nao houver Visual C++ ou se o instalado for MAIS VELHO
  que o que vai aqui (o motor precisa de DLLs que so as versoes novas tem,
  como vcruntime140_threads.dll). Roda em silencio (/install /quiet
  /norestart). Resultado 0 = instalou; 1638 = ja havia versao mais nova;
  3010 = instalou e pede reiniciar (o instalador avisa no fim). Qualquer
  outro: o programa e instalado mesmo assim, com um aviso em portugues de que
  o detector de linhas Kraken pode nao funcionar.

  Arriscado mudar: a chave e os nomes dos valores (sao os da Microsoft); os
  parametros do vc_redist. }

var
  PrecisaReiniciar: Boolean;

function LerVersao(Raiz: Integer; var Maior, Menor, Build: Cardinal): Boolean;
var
  Instalado: Cardinal;
  Chave: String;
begin
  Result := False;
  Chave := 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64';
  if RegQueryDWordValue(Raiz, Chave, 'Installed', Instalado) and (Instalado = 1) then
    if RegQueryDWordValue(Raiz, Chave, 'Major', Maior) and
       RegQueryDWordValue(Raiz, Chave, 'Minor', Menor) and
       RegQueryDWordValue(Raiz, Chave, 'Bld', Build) then
      Result := True;
end;

function MaisNova(Ma1, Mi1, Bl1, Ma2, Mi2, Bl2: Cardinal): Boolean;
begin
  if Ma1 <> Ma2 then Result := Ma1 > Ma2
  else if Mi1 <> Mi2 then Result := Mi1 > Mi2
  else Result := Bl1 > Bl2;
end;

function PrecisaDoVisualC(): Boolean;
var
  Ma, Mi, Bl, Ma2, Mi2, Bl2: Cardinal;
  Achou: Boolean;
begin
  Achou := False;
  Ma := 0; Mi := 0; Bl := 0;
  if LerVersao(HKLM64, Ma2, Mi2, Bl2) then begin
    Achou := True; Ma := Ma2; Mi := Mi2; Bl := Bl2;
  end;
  if LerVersao(HKLM32, Ma2, Mi2, Bl2) then begin
    if (not Achou) or MaisNova(Ma2, Mi2, Bl2, Ma, Mi, Bl) then begin
      Ma := Ma2; Mi := Mi2; Bl := Bl2;
    end;
    Achou := True;
  end;
  if Achou then
    Log(Format('Visual C++ x64 instalado: %d.%d.%d; o do instalador: {#VcMaior}.{#VcMenor}.{#VcBuild}', [Ma, Mi, Bl]))
  else
    Log('Visual C++ x64 nao encontrado no registro');
  Result := (not Achou) or MaisNova({#VcMaior}, {#VcMenor}, {#VcBuild}, Ma, Mi, Bl);
end;

procedure InstalarVisualC();
var
  Codigo: Integer;
begin
  if not PrecisaDoVisualC() then begin
    Log('Visual C++: ja instalado, pulando');
    Exit;
  end;
  WizardForm.StatusLabel.Caption :=
    'Instalando uma peça da Microsoft que o programa precisa (pode levar um minuto)...';
  ExtractTemporaryFile('vc_redist.x64.exe');
  if not Exec(ExpandConstant('{tmp}\vc_redist.x64.exe'), '/install /quiet /norestart', '',
              SW_HIDE, ewWaitUntilTerminated, Codigo) then
    Codigo := -1;
  Log(Format('vc_redist.x64.exe terminou com o codigo %d', [Codigo]));
  if Codigo = 3010 then
    PrecisaReiniciar := True
  else if (Codigo <> 0) and (Codigo <> 1638) then
    SuppressibleMsgBox(
      'Não foi possível instalar uma peça da Microsoft (Visual C++) que o detector de linhas ' +
      'Kraken usa. O programa foi instalado e funciona, mas esse detector pode ficar desligado.' + #13#10#13#10 +
      'Tente instalar de novo. Se continuar, avise quem cuida do programa (código ' +
      IntToStr(Codigo) + ').', mbInformation, MB_OK, IDOK);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    InstalarVisualC();
end;

function NeedRestart(): Boolean;
begin
  Result := PrecisaReiniciar;
end;
