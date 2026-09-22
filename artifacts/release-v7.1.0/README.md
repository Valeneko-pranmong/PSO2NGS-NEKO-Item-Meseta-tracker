# 🌸 NEKO Item & Meseta Tracker — Release v7.1.0 Distribution Artifacts

> **สถานะ:** `[CURRENT]` 🟢 — ไฟล์ติดตั้งและชุดแพ็กเกจทางการสำหรับผู้ใช้งานจริงและเครื่องทดสอบ (Active Production & Testing Distribution)  
> **รุ่น:** Python Version `7.1.0` (Pure Python Modular Engine with ARKS War Room & Multi-Language Support)  
> **ผู้พัฒนา:** NEKO FAMILY TEAM SHIP 4 JP / Vale3neko  
> **แพลตฟอร์ม:** Windows 10 / Windows 11 (64-bit)

---

## 📦 ตารางจำแนกสถานะอาร์ติแฟกต์ (Artifact Lifecycle Classification)

| ไฟล์อาร์ติแฟกต์ (Artifact Name) | สถานะ (Tier) | บทบาทและรายละเอียด |
| :--- | :--- | :--- |
| **`NekoTracker-Setup-v7.1.0.exe`** | `[CURRENT]` 🟢 | **ใช้งานจริงและทดสอบ (Active):** ตัวติดตั้งแบบ Single-EXE Installer สำหรับผู้ใช้งานทั่วไปและเครื่องทดสอบ (ครอบคลุมตัวแอปหลัก Python V7.1.0, คู่มือ 3 ภาษา, ระบบ Uninstaller 4 ช่องทาง) |
| **`SHA256SUMS.txt`** | `[CURRENT]` 🟢 | **ตรวจสอบความถูกต้อง (Verification):** ค่าแฮชทางคณิตศาสตร์ SHA-256 เพื่อความโปร่งใสและตรวจสอบความสมบูรณ์ของไฟล์ |
| **`E2E_TEST_CHECKLIST.md`** | `[CURRENT]` 🟢 | **คู่มือเช็กลิสต์ QA (Testing):** แบบฟอร์มเช็กลิสต์การทดสอบ E2E สำหรับมนุษย์/คนเทส เริ่มตั้งแต่ตัวติดตั้งจนถึงถอนการติดตั้ง |
| **`../portable-test-v7.1.0/`** | `[REFERENCE]` 🔵 | **เก็บอ้างอิง (Reference):** โครงสร้างแพ็กเกจแบบ Portable สำหรับทดสอบก่อนคอมไพล์ตัวติดตั้ง |
| **`../release-v6.1.0/`** | `[ARCHIVE]` 🔴 | **เวอร์ชันเก่า (Archived Release):** ชุดติดตั้งรุ่นก่อนหน้าที่ปลดระวางแล้ว |
| **`../release-v7.0.0-alpha/`** | `[ARCHIVE]` 🔴 | **เวอร์ชันเก่า (Archived Release):** ชุดติดตั้งรุ่นทดลองเดิมที่ถูกระงับ (Revoked) |

---

## 🛡️ ลายเซ็นดิจิทัลและแฮชความปลอดภัย (Cryptographic Checksums)

ตรวจสอบความถูกต้องของไฟล์ก่อนการใช้งานด้วยค่า SHA-256:

```text
de3165db2c026ce1fff02b544a74430a11c830118c875a689ed05c65b4e1bd72  NekoTracker-Setup-v7.1.0.exe
```

* **ขนาดไฟล์:** ~22.19 MB
* **กลไกการบีบอัด:** LZMA2/Ultra64 Solid Compression (Inno Setup 6)
* **สถาปัตยกรรม:** 64-bit Windows (`ArchitecturesAllowed=x64compatible`)
* **การติดตั้ง:** Per-User Local AppData (`%LOCALAPPDATA%\NEKO FAMILY\NekoTracker`, `PrivilegesRequired=lowest`) ไม่ต้องใช้สิทธิ์ Administrator ไม่เด้งเตือน UAC
* **ระบบความปลอดภัย:** 100% TOS Safe (Passive File Ingestion Only) + Zero-Login Architecture

---

## 🚀 จุดเด่นในตัวติดตั้ง V7.1.0 สำหรับเครื่องเทสและผู้ใช้ทั่วไป

### 1. ระบบตัวโปรแกรมหลัก (Production Tracker — V7.1.0)
- **Zero-Login Architecture:** ดึงชื่อตัวละคร `CharacterName` และ `PlayerID` จาก `ActionLog` อัตโนมัติ ปลอดภัย 100% ไม่ถามรหัสผ่าน
- **Real-Time Meseta & Drops:** คำนวณรายได้สุทธิ, อัตราความเร็วเงินต่อชั่วโมง (M/hr) และรายการไอเท็มดรอป
- **Multi-Language Support (3 ภาษา):** สลับภาษาอังกฤษ (English), ไทย (ไทย), และญี่ปุ่น (日本語) ได้สดทันที
- **In-App User Guide:** หน้าต่างคู่มือการใช้งานและคำแนะนำระบบสงครามในตัว รองรับ 3 ภาษา พร้อมปุ่มคัดลอกลิงก์ Discord คอมมูนิตี้
- **ARKS War Room (Coordinate War Engine V9):** รองรับพิกัด 798 Sectors และ 4 Quadrant Slots พร้อมระบบ Standby Presence และซิงค์สด Realtime ขึ้น Cloud
- **AntiTamperGuard V7.1.0:** 10 เกราะป้องกันความสมบูรณ์ของข้อมูลและเพิกถอนเวอร์ชันที่มีช่องโหว่
- **แก้ไขปุ่มพับจอ (Window Minimize Fix):** ปรับปรุง Event Loop ดักจับสถานะ `<Map>` ขณะ Minimize ให้หน้าต่างย่อลง Taskbar ได้อย่างสมบูรณ์ ไม่เด้งกลับขึ้นมาเอง

### 2. ชุดเครื่องมือและแพ็กเกจสำหรับเครื่องทดสอบอื่นๆ (Testing on Other Machines)
- **Native Test Mode Support (`--test` / `NEKO_TEST_MODE=1`):** ข้ามการตรวจจับ Process ของเกม (`pso2.exe`), File Handle, Timestamp Skew, และ Velocity Limit สำหรับเครื่องที่ไม่มีตัวเกม PSO2 NGS ทำให้ทดสอบยอด Meseta และส่งข้อมูลขึ้นคลาวด์ได้ 100%
- **Smart Sample Log Ingestion:** เมื่อเปิดโฟลเดอร์ชื่อ `sample_logs` หรือโฟลเดอร์ที่มีไฟล์ทดสอบ ระบบจะเข้าสู่ Test Mode อัตโนมัติ ป้ายเหลือง `[TEST MODE]` ปรากฏ และอ่านข้อมูลได้ทันที
- **Portable Test Package (`NekoTracker-v7.1.0-Portable-Test.zip`):** สำหรับเครื่องทดสอบที่ไม่มีเกม PSO2 หรือไม่มี Python มีชุดไฟล์ Standalone พร้อมตัวจำลอง `NekoLogSimulator.exe`, โฟลเดอร์ `sample_logs/`, และสคริปต์ 1-Click Launchers:
  - `3_Quick_Test_All_In_One.bat` — รันตัวสตรีมข้อมูลจำลองสด + เปิด NekoTracker พร้อมกันทันที
  - `1_Run_NekoTracker_Test.bat` — รันตัวโปรแกรม NekoTracker ในโหมด Standalone Test
  - `2_Start_Mock_Log_Feed.bat` — รันสตรีมเมอร์จำลอง ActionLog สด

---

## 📖 วิธีการติดตั้งและทดสอบ (Installation & Testing Guide)

### 🇹🇭 ภาษาไทย (TH)

#### ก. การติดตั้งปกติ (สำหรับเครื่องที่มีเกม PSO2:NGS)
1. นำไฟล์ `NekoTracker-Setup-v7.1.0.exe` ไปยังเครื่องเป้าหมาย
2. ดับเบิลคลิกเพื่อเริ่มการติดตั้ง (ไม่ต้องกด Run as administrator)
3. กด Next เพื่อติดตั้งลงใน `%LOCALAPPDATA%\NEKO FAMILY\NekoTracker`
4. เมื่อติดตั้งเสร็จ สามารถเปิด **NEKO Item & Meseta Tracker** โปรแกรมจะค้นหาโฟลเดอร์ Log ของเกมโดยอัตโนมัติ

#### ข. การทดสอบบนเครื่องทดสอบอื่น (ไม่มีเกมหรือไม่มี Python)
สามารถเลือกทดสอบได้ 2 รูปแบบตามความสะดวก:
* **รูปแบบที่ 1 (ทดสอบตัวติดตั้ง Release Candidate):**
  1. ดับเบิลคลิก `NekoTracker-Setup-v7.1.0.exe` เพื่อติดตั้ง
  2. เปิดโปรแกรมจาก Desktop หรือ Start Menu
  3. คลิกปุ่ม **"เลือกโฟลเดอร์ Log"** แล้วเลือกโฟลเดอร์ `sample_logs` (คัดลอกจากชุดทดสอบ)
  4. ป้ายสถานะ `[TEST MODE]` สีเหลืองจะปรากฏ และประมวลผลข้อมูลจำลองทันที
* **รูปแบบที่ 2 (ทดสอบทันทีแบบไม่ต้องติดตั้ง Portable Test):**
  1. แตกไฟล์ `NekoTracker-v7.1.0-Portable-Test.zip`
  2. ดับเบิลคลิก `3_Quick_Test_All_In_One.bat`
  3. ระบบจะเปิด Live Mock Streamer (`NekoLogSimulator.exe`) และเปิดตัวแอปให้พร้อมทดสอบทันทีโดยไม่ต้องติดตั้งและไม่ต้องมี Python

---

### 🇬🇧 English (EN)

#### A. Standard Installation (For Machines with PSO2:NGS Installed)
1. Transfer `NekoTracker-Setup-v7.1.0.exe` to target machine.
2. Double-click the installer (no admin elevation required).
3. Proceed with the setup wizard to install into `%LOCALAPPDATA%\NEKO FAMILY\NekoTracker`.
4. Launch **NEKO Item & Meseta Tracker**; log folder will be auto-detected.

#### B. Testing on Clean / Non-Game Machines
* **Option 1 (Test Official Release Candidate Installer):**
  1. Run `NekoTracker-Setup-v7.1.0.exe` and complete installation.
  2. Launch from Desktop or Start Menu.
  3. Click **"Select Log Folder"** and choose a `sample_logs` directory.
  4. The `[TEST MODE]` yellow badge will activate and simulate telemetry cleanly.
* **Option 2 (Instant Zero-Install Portable Test Bundle):**
  1. Extract `NekoTracker-v7.1.0-Portable-Test.zip`.
  2. Run `3_Quick_Test_All_In_One.bat`.
  3. Built-in `NekoLogSimulator.exe` streams live mock drops, launching the tracker instantly without Python or NGS installed.
