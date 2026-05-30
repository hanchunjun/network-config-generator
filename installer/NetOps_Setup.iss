; ============================================================
; NetOps 企业网络自动化运维平台 - Inno Setup 安装脚本
; ============================================================
; 使用方法：
;   1. 先执行 pyinstaller NetworkConfigGenerator.spec --noconfirm 生成 dist/NetOps/
;   2. 用 Inno Setup 6 打开本脚本，编译即可生成安装包
;   3. 输出：installer/NetOps_Setup_0.4.0.exe
; ============================================================

#define MyAppName "NetOps"
#define MyAppFullName "NetOps 企业网络自动化运维平台"
#define MyAppVersion "0.4.0"
#define MyAppPublisher "NetOps"
#define MyAppExeName "NetOps.exe"

[Setup]
; 应用基本信息
AppId={{B2A3D5E8-7F1C-4A9E-B6D3-E8F2C1A5B9D7}
AppName={#MyAppFullName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppSupportURL=https://github.com/hanchunjun/network-config-generator
; 安装目录（默认 Program Files\NetOps）
DefaultDirName={autopf}\NetOps
DefaultGroupName=NetOps
; 安装包输出
OutputDir=..\installer
OutputBaseFilename=NetOps_Setup_{#MyAppVersion}
; 压缩
Compression=lzma2/ultra64
SolidCompression=yes
; 外观
WizardStyle=modern
SetupIconFile=..\assets\netops.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
; 权限（最低权限安装，用户可选管理员）
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
; 卸载时保留用户数据（config/projects/single/activation 目录）
; 通过 [Dirs] 的 uninsneveruninstall 标志实现

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加选项:"
Name: "quicklaunchicon"; Description: "创建快速启动栏快捷方式"; GroupDescription: "附加选项:"; Flags: unchecked

[Files]
; PyInstaller --onedir 构建产物（主程序 + 全部依赖）
Source: "..\dist\NetOps\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; AI Agent 提示词文件
Source: "..\agents\*"; DestDir: "{app}\agents"; Flags: ignoreversion recursesubdirs createallsubdirs
; 运维脚本（备份/巡检/故障核查）
Source: "..\scripts\backup_all_config.py"; DestDir: "{app}\scripts"; Flags: ignoreversion
Source: "..\scripts\network_inspect.py"; DestDir: "{app}\scripts"; Flags: ignoreversion
Source: "..\scripts\run_trouble_cmd.py"; DestDir: "{app}\scripts"; Flags: ignoreversion
Source: "..\scripts\__init__.py"; DestDir: "{app}\scripts"; Flags: ignoreversion

[Dirs]
; 运行时数据目录（首次启动自动创建，预建确保写入权限）
Name: "{app}\config"; Flags: uninsneveruninstall
Name: "{app}\logs"; Flags: uninsneveruninstall
Name: "{app}\projects"; Flags: uninsneveruninstall
Name: "{app}\single"; Flags: uninsneveruninstall
Name: "{app}\activation"; Flags: uninsneveruninstall

[Icons]
; 开始菜单快捷方式
Name: "{group}\{#MyAppFullName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "启动 NetOps"
Name: "{group}\卸载 NetOps"; Filename: "{uninstallexe}"
; 桌面快捷方式
Name: "{autodesktop}\{#MyAppFullName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
; 快速启动栏
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppFullName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; 安装完成后可选启动
Filename: "{app}\{#MyAppExeName}"; Description: "启动 NetOps 企业网络自动化运维平台"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 卸载时清理日志（用户数据 config/projects/single/activation 保留）
Type: filesandordirs; Name: "{app}\logs"
