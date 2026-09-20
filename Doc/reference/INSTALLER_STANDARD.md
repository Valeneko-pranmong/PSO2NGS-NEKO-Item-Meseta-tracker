# 📦 NEKO FAMILY — มาตรฐานกลางระบบติดตั้งซอฟต์แวร์ Windows (Installer Standard)

> **สถานะ:** `[REFERENCE]` 🔵 — เอกสารข้อกำหนดมาตรฐานกลางสำหรับระบบตัวติดตั้ง (Authoritative Installer Standard)  
> **มาตรฐานอ้างอิง:** ถอดแบบและสอดคล้องกับสถาปัตยกรรม `Neko-Family-Proxy`  
> **กลุ่มเป้าหมาย:** ซอฟต์แวร์ในเครือ **NEKO FAMILY** บนระบบปฏิบัติการ Windows 10 และ Windows 11 (64-bit)

---

## 1. ปรัชญาและหลักการสำคัญ (Core Principles)

ระบบตัวติดตั้งสำหรับซอฟต์แวร์ในเครือ NEKO FAMILY ยึดถือหลักการออกแบบดังต่อไปนี้:

1. **Per-User Deployment (การติดตั้งระดับผู้ใช้ ไม่ต้องขอสิทธิ์ Admin พร่ำเพรื่อ):**
   * ติดตั้งลงในโฟลเดอร์ Application Data ของผู้ใช้ (`%LOCALAPPDATA%\NEKO FAMILY\<AppSlug>\`) เสมอ
   * ใช้ค่าคอนฟิก `PrivilegesRequired=lowest` เพื่อให้ผู้ใช้สามารถดับเบิลคลิกติดตั้งได้ทันที **โดยไม่มีหน้าต่าง UAC เด้งกวนใจ**
   * ป้องกันปัญหา Permission Denied เมื่อโปรแกรมต้องการสร้างไฟล์แคช, คอนฟิก, หรืออ่าน/เขียนไฟล์ Log ภายในโฟลเดอร์ตนเอง
2. **Primary Application Integrity (ความสมบูรณ์ของตัวโปรแกรมหลัก):**
   * ไฟล์ `.exe` ตัวหลักที่สร้างขึ้นใน Root `{app}` และชอร์ตคัตบน **Desktop** / **Start Menu** จะต้องเป็น **ตัวโปรแกรมหลักจริง (Production Application)** ที่ผู้ใช้คาดหวังเสมอ
   * ห้ามสลับหรือนำตัวทดลอง/ตัวพรีวิว (Alpha Preview / Companion) มาเป็นตัวเปิดหลักเด็ดขาด หากมีตัวพรีวิว ให้แยกโฟลเดอร์ย่อย เช่น `{app}\wpf-preview\`
3. **Fail-Closed Pre-flight Gates (ผ่านการทดสอบ 100% ก่อนเริ่มบิลด์):**
   * สคริปต์ควบคุมการบิลด์ (`build_installer.py`) จะต้องรันชุดทดสอบอัตโนมัติ (Automated Unit Tests / Integration Tests) ทั้งหมดก่อนเสมอ หากมีข้อสอบตกแม้แต่ข้อเดียว กระบวนการบิลด์จะต้องหยุดทำงานทันที (Fail-Closed)
4. **Strict Architecture Enforcement (จำกัดสถาปัตยกรรม 64-bit เท่านั้น):**
   * กำหนด `ArchitecturesAllowed=x64compatible` และ `ArchitecturesInstallIn64BitMode=x64compatible` เพื่อล็อกให้รันได้เฉพาะบน Windows 64-bit แท้ ป้องกันปัญหาความเข้ากันไม่ได้ของไลบรารี C/C++ หรือ Python DLLs
5. **Automated Lifecycle & Process Smoke Test (ทดสอบติดตั้งจริงและรัน Process Smoke):**
   * ทุกครั้งที่คอมไพล์ตัวติดตั้งสำเร็จ ระบบบิลด์อัตโนมัติจะต้องทำการติดตั้งเงียบ (`/VERYSILENT`) ลงใน Sandbox ชั่วคราว
   * สั่งรันไฟล์ `.exe` ตัวจริง และเฝ้ามอง Process ID (PID) เป็นเวลาอย่างน้อย 3 วินาที เพื่อยืนยันว่าโปรแกรมเปิดขึ้นมาได้จริง ไม่แครช (Zero Immediate Crash)
   * สั่งรัน Uninstaller เพื่อตรวจสอบว่าสามารถถอนการติดตั้งได้อย่างสะอาดหมดจด

---

## 2. โครงสร้างโฟลเดอร์มาตรฐานของระบบติดตั้ง (Installer Directory Layout)

ในทุกคลังโค้ดของ NEKO FAMILY ที่มีระบบตัวติดตั้ง ให้จัดวางโครงสร้างโฟลเดอร์ดังนี้:

```text
<repository-root>/
├── installer/
│   ├── <AppName>.iss           # สคริปต์หลัก Inno Setup 6 (คอนฟิก UI, ไฟล์, ชอร์ตคัต, ถอนการติดตั้ง)
│   ├── build_installer.py      # Python Orchestrator: ทดสอบ -> แพ็กเกจ -> คอมไพล์ -> แฮช -> Smoke Test
│   ├── LICENSE.txt             # ข้อกำหนดสิทธิ์และสัญญาอนุญาตการใช้งาน
│   └── README.md               # คู่มือการใช้งานระบบตัวติดตั้งประจำคลัง
├── build_installer.bat         # สคริปต์ Batch สำหรับเรียก build_installer.py ด้วยการดับเบิลคลิกเดียว
├── artifacts/
│   └── release-<version>/      # ไดเรกทอรีเก็บอาร์ติแฟกต์สำเร็จรูปทางการ
│       ├── <App>-Setup-<version>.exe  # ตัวติดตั้งสมบูรณ์ Single-EXE
│       ├── SHA256SUMS.txt      # ลายเซ็นดิจิทัลค่าแฮช SHA-256
│       └── README.md           # ตารางกำกับสถานะอาร์ติแฟกต์ (Current / Reference / Archive)
```

---

## 3. รายละเอียดการตั้งค่า Inno Setup (`.iss`) มาตรฐาน

### 3.1 การประกาศ Metadata และไดเรกทอรีติดตั้ง

```iss
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

; [มาตรฐาน NEKO] ติดตั้งระดับผู้ใช้ใน LocalAppData
DefaultDirName={localappdata}\NEKO FAMILY\NekoTracker
DefaultGroupName={#MyAppName}
DisableDirPage=no
DisableProgramGroupPage=yes
UsePreviousAppDir=yes

; [มาตรฐาน NEKO] ไม่ต้องขอสิทธิ์ Administrator (Zero UAC)
PrivilegesRequired=lowest

; [มาตรฐาน NEKO] บล็อกสถาปัตยกรรมที่ไม่ใช่ x64 แท้
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; [มาตรฐาน NEKO] การบีบอัดสูงสุด
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
```

### 3.2 การกระจายไฟล์ (Files Placement)

* **โปรแกรมหลัก:** แตกไฟล์จากโฟลเดอร์ Distribution (เช่น `..\dist\NekoTracker\*`) ลงที่ `{app}` โดยตรง
* **ไอคอนและโลโก้:** คัดลอก `icon.ico` และ `logo.png` ลงที่ `{app}`
* **เอกสาร:** คัดลอก `LICENSE.txt` และ `README.md` ลงที่ `{app}`
* **ตัวทดลองเสริม (Optional Preview):** หากมี ให้วางไว้ในโฟลเดอร์ย่อย เช่น `{app}\wpf-preview\` พร้อมเงื่อนไข `Check: DirExists(...)`

```iss
[Files]
Source: "..\dist\NekoTracker\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\logo.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; DestName: "README.md"; Flags: ignoreversion
```

### 3.3 การสร้างทางลัด (Shortcuts & Icons)

* สร้างชอร์ตคัตบน Start Menu: `{autoprograms}\{#MyAppName}`
* สร้างชอร์ตคัตบน Desktop: `{autodesktop}\{#MyAppName}`
* ชอร์ตคัตสำหรับถอนการติดตั้ง: `{autoprograms}\{cm:UninstallProgram,{#MyAppName}}`

```iss
[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; WorkingDir: "{app}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; WorkingDir: "{app}"; Tasks: desktopicon
Name: "{autoprograms}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
```

### 3.4 การทำความสะอาดเมื่อถอนการติดตั้ง (Clean Uninstaller)

จะต้องระบุรายการไฟล์แคช, ไดเรกทอรีย่อยชั่วคราว (`__pycache__`, `_internal`), และไฟล์คอนฟิกให้ถูกลบออกอย่างหมดจด:

```iss
[UninstallDelete]
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\ngs_tracker_config.json"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\_internal"
Type: filesandordirs; Name: "{app}\wpf-preview"
Type: dirifempty; Name: "{app}"
```

---

## 4. ไปป์ไลน์สคริปต์ควบคุมการบิลด์ (`build_installer.py`)

สคริปต์ `build_installer.py` ต้องดำเนินการตามลำดับขั้น 6 ขั้นตอน (6-Step Fail-Closed Workflow) ดังนี้:

```text
┌──────────────────────────────────────────────────────────────┐
│ 1. Pre-flight Tests Gate (pytest + dotnet test)              │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. Application Packaging (PyInstaller onedir / dotnet)       │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. Inno Setup Compilation (ISCC.exe -> Setup.exe)            │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. Cryptographic Hashing (SHA-256 -> SHA256SUMS.txt)         │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. Automated Lifecycle Smoke Test (Silent Install Sandbox)   │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ 6. Process Smoke & Clean Uninstall Verification              │
└──────────────────────────────────────────────────────────────┘
```

### 4.1 รายละเอียดการทดสอบ Process Smoke Test
1. เรียกใช้ตัวติดตั้งด้วยพารามิเตอร์แบบเงียบ:
   ```bash
   NekoTracker-Setup-<version>.exe /VERYSILENT /SUPPRESSMSGBOXES /DIR=<sandbox_dir>
   ```
2. ตรวจสอบว่ามีไฟล์ `NekoTracker.exe` และ `unins000.exe` อยู่จริง
3. รันโปรแกรมผ่าน `subprocess.Popen([installed_main_exe])`
4. รอ 3 วินาที แล้วตรวจสอบว่า `proc.poll() is None` (โปรแกรมยังคงรันอยู่ ไม่หลุดหรือแครช)
5. สั่งปิด Process ด้วย `proc.terminate()`
6. เรียก `unins000.exe /VERYSILENT /SUPPRESSMSGBOXES` แล้วยืนยันว่าไดเรกทอรีและไฟล์โปรแกรมถูกล้างออกอย่างหมดจด

---

## 5. การตรวจสอบความถูกต้องและการเผยแพร่ (Release Governance)

1. **ห้าม Commit ตัวไฟล์ `Setup.exe` และโฟลเดอร์ `build/` เข้า Git:**
   * ตรวจสอบว่า `.gitignore` ได้ระบุ `artifacts/**/*.exe`, `build/`, และ `dist/` ไว้อย่างถูกต้อง
2. **ไฟล์ที่ต้อง Commit เพื่อยืนยัน Release:**
   * `artifacts/release-<version>/SHA256SUMS.txt`
   * `artifacts/release-<version>/README.md`
   * สคริปต์ `installer/<AppName>.iss` และ `installer/build_installer.py`
3. **การนำส่งผู้ใช้ทั่วไป:**
   * ผู้ใช้ดาวน์โหลดไฟล์ `NekoTracker-Setup-<version>.exe` เพียงไฟล์เดียว แล้วดับเบิลคลิกติดตั้งเพื่อใช้งานได้ทันที 100%
