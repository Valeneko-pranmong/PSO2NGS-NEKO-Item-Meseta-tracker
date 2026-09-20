; ==============================================================================
; NEKO Item & Meseta Tracker - Inno Setup Script
; Author: NEKO FAMILY TEAM SHIP 4 JP / Vale3neko
; Target Platform: Windows 10 / Windows 11 (64-bit)
; Architecture: Per-User Local AppData (NEKO FAMILY Standard)
; Version: 6.1.0 (Python Modular Engine with ARKS War Room & Firebase Sync)
; ==============================================================================

#define MyAppName "NEKO Item & Meseta Tracker"
#define MyAppVersion "6.1.0"
#define MyAppPublisher "NEKO FAMILY"
#define MyAppURL "https://github.com/Vale3neko/PSO2NGS-NEKO-Item-Meseta-tracker"
#define MyAppExeName "NekoTracker.exe"

[Setup]
AppId={{D37E84B1-29C1-4D04-8E8E-27FF7A5B69C1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Per-user Local AppData topology (NEKO FAMILY standard: PrivilegesRequired=lowest)
DefaultDirName={localappdata}\NEKO FAMILY\NekoTracker
DefaultGroupName={#MyAppName}
DisableDirPage=no
DisableProgramGroupPage=yes
UsePreviousAppDir=yes

; Non-elevated per-user installation (Zero UAC prompt required)
PrivilegesRequired=lowest

; Hard block non-x64 host (strict 64-bit enforcement)
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

OutputDir=..\artifacts\release-v6.1.0
OutputBaseFilename=NekoTracker-Setup-v6.1.0
SetupIconFile=..\icon.ico
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
Uninstallable=yes
CloseApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Primary Application: Python Tracker (PyInstaller Onedir Distribution)
Source: "..\dist\NekoTracker\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Root Assets and Icons
Source: "..\icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\logo.png"; DestDir: "{app}"; Flags: ignoreversion
; Documentation & License
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; DestName: "README.md"; Flags: ignoreversion

[Icons]
; Start Menu Shortcuts
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; WorkingDir: "{app}"
Name: "{autoprograms}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
; Desktop Shortcut
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[InstallDelete]
Type: files; Name: "{app}\*.log"

[UninstallDelete]
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\ngs_tracker_config.json"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\_internal"
Type: dirifempty; Name: "{app}"
