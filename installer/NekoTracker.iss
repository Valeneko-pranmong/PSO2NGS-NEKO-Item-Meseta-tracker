; ==============================================================================
; NEKO Item & Meseta Tracker - Inno Setup Script (Production E2E Release)
; Author: NEKO FAMILY TEAM SHIP 4 JP / Vale3neko
; Target Platform: Windows 10 / Windows 11 (64-bit)
; Architecture: Per-User Local AppData (NEKO FAMILY Standard)
; Version: 7.1.0 (Python Modular Engine with ARKS War Room & Multi-Language)
; ==============================================================================

#define MyAppName "NEKO Item & Meseta Tracker"
#define MyAppVersion "7.1.0"
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

OutputDir=..\artifacts\release-v7.1.0
OutputBaseFilename=NekoTracker-Setup-v7.1.0
SetupIconFile=..\icon.ico
UninstallDisplayName={#MyAppName} (v{#MyAppVersion})
UninstallDisplayIcon={app}\{#MyAppExeName}
Uninstallable=yes
CreateUninstallRegKey=yes
CloseApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "uninstallicon"; Description: "Create Desktop shortcut for Uninstaller (ถอนการติดตั้ง)"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Primary Application: Python Tracker (PyInstaller Onedir Distribution)
Source: "..\dist\NekoTracker\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Root Assets and Icons
Source: "..\icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\logo.png"; DestDir: "{app}"; Flags: ignoreversion
; User Documentation & License
Source: "..\Doc\current\HOW_TO_USE.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; DestName: "README.md"; Flags: ignoreversion
; Uninstaller Helper Launcher
Source: "Uninstall.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu Shortcuts
Name: "{autoprograms}\{#MyAppName}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; WorkingDir: "{app}"
Name: "{autoprograms}\{#MyAppName}\User Guide (HOW TO USE)"; Filename: "{app}\HOW_TO_USE.md"; WorkingDir: "{app}"
Name: "{autoprograms}\{#MyAppName}\Uninstall (ถอนการติดตั้ง) {#MyAppName}"; Filename: "{uninstallexe}"; IconFilename: "{app}\icon.ico"
Name: "{autoprograms}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; IconFilename: "{app}\icon.ico"

; Desktop Shortcuts
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; WorkingDir: "{app}"; Tasks: desktopicon
Name: "{autodesktop}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; IconFilename: "{app}\icon.ico"; Tasks: uninstallicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[InstallDelete]
Type: files; Name: "{app}\*.log"

[UninstallDelete]
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\*.bat"
Type: files; Name: "{app}\ngs_tracker_config.json"
Type: filesandordirs; Name: "{app}\fonts"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\_internal"
Type: dirifempty; Name: "{app}"
