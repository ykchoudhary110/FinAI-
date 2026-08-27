; FinAI Windows Installer Script (Inno Setup 6.x)
; Master build script for FinAI — Offline Financial AI Assistant

[Setup]
AppName=FinAI — Offline Financial AI Assistant
AppVersion=1.0.0
AppPublisher=FinAI Engineering Team
DefaultDirName={autopf}\FinAI
DefaultGroupName=FinAI
OutputDir=dist_installer
OutputBaseFilename=FinAI_Setup
Compression=lzma2/max
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\finai.exe
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\finai\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\FinAI"; Filename: "{app}\finai.exe"
Name: "{group}\Uninstall FinAI"; Filename: "{uninstallexe}"
Name: "{autodesktop}\FinAI"; Filename: "{app}\finai.exe"; Tasks: desktopicon

[Run]
Filename: "ollama"; Parameters: "pull qwen2.5:3b"; StatusMsg: "Downloading local AI model (Qwen 2.5 3B)... This may take a few minutes."; Flags: runhidden runascurrentuser; Check: IsOllamaInstalled
Filename: "{app}\finai.exe"; Description: "Launch FinAI Assistant"; Flags: postinstall nowait skipifsilent

[Code]
function IsOllamaInstalled: Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('ollama', '--version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;
