; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "SpotiScrape"
#define MyAppVersion "1.5.0"
#define MyAppPublisher "Marco Antonio Tecson"
#define MyAppURL "https://github.com/Mordical62645"
#define MyAppExeName "spotiscrape.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{5B329BC0-4461-47B6-A79B-527015359050}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
; "ArchitecturesAllowed=x64compatible" specifies that Setup cannot run
; on anything but x64 and Windows 11 on Arm.
ArchitecturesAllowed=x64compatible
; "ArchitecturesInstallIn64BitMode=x64compatible" requests that the
; install be done in "64-bit mode" on x64 or Windows 11 on Arm,
; meaning it should use the native 64-bit Program Files directory and
; the 64-bit view of the registry.
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
LicenseFile=C:\Users\ptecs\OneDrive\Documents\COLLEGE\3RD YEAR\1ST SEMESTER\SUBJECTS\CY1\PC14\ACTIVITIES\OCTOBER\October 23, 2024\Spotiscrape\license.txt
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
OutputDir=C:\Users\ptecs\OneDrive\Documents\COLLEGE\3RD YEAR\1ST SEMESTER\SUBJECTS\CY1\PC14\ACTIVITIES\OCTOBER\October 23, 2024\Spotiscrape
OutputBaseFilename=SpotiScrape_WINDOWS_1.5_setup
SetupIconFile=C:\Users\ptecs\Downloads\Windows_Installer_icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\ptecs\OneDrive\Documents\COLLEGE\3RD YEAR\1ST SEMESTER\SUBJECTS\CY1\PC14\ACTIVITIES\OCTOBER\October 23, 2024\Spotiscrape\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

