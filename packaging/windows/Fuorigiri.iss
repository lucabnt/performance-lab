#ifndef AppVersion
  #define AppVersion "0.10.0"
#endif
[Setup]
AppId={{A491CC28-F146-4D8B-A7AD-AB4B8E3CA922}
AppName=Fuorigiri Performance Lab
AppVersion={#AppVersion}
AppPublisher=Luca Bontempi
DefaultDirName={localappdata}\Programs\Fuorigiri
DefaultGroupName=Fuorigiri Performance Lab
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.19045
WizardStyle=modern
LicenseFile=..\..\LICENSE
SetupIconFile=..\..\frontend\public\branding\fuorigiri.ico
UninstallDisplayIcon={app}\Fuorigiri.exe
OutputDir=..\..\dist\release
OutputBaseFilename=Fuorigiri-{#AppVersion}-windows-x64-setup
Compression=lzma2/normal
SolidCompression=yes
CloseApplications=yes
RestartApplications=no
UsePreviousAppDir=yes
DisableProgramGroupPage=yes

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\..\dist\Fuorigiri\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Tasks]
Name: "desktopicon"; Description: "Crea un collegamento sul desktop"; Flags: unchecked

[Icons]
Name: "{autoprograms}\Fuorigiri Performance Lab"; Filename: "{app}\Fuorigiri.exe"; AppUserModelID: "Fuorigiri.PerformanceLab"
Name: "{autodesktop}\Fuorigiri Performance Lab"; Filename: "{app}\Fuorigiri.exe"; Tasks: desktopicon; AppUserModelID: "Fuorigiri.PerformanceLab"

[Run]
Filename: "{app}\Fuorigiri.exe"; Description: "Avvia Fuorigiri Performance Lab"; Flags: nowait postinstall skipifsilent
