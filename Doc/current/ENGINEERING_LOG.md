# 📜 NEKO Item & Meseta Tracker — Engineering History Log (บันทึกประวัติวิศวกรรม)

> **สถานะ:** `[CURRENT]` 🟢 — บันทึกประวัติวิศวกรรมและวิวัฒนาการสถาปัตยกรรมระบบ (Maintained Engineering History)  
> **เก็บบันทึกโดย:** NEKO FAMILY Engineering Team / Vale3neko  

---

## 📅 ลำดับเหตุการณ์และประวัติการพัฒนา (Chronological Milestones)

### Milestone 1: จุดเริ่มต้นโครงการและ V6.0.0 Release (`b96b646`, `54327e0`)
* **ขอบเขต:** พัฒนาเครื่องมือติดตาม N-Meseta สำหรับเกม Phantasy Star Online 2: New Genesis (PSO2:NGS)
* **การออกแบบหลัก:**
  - ทำงานแบบ 100% Offline ไม่มีการส่งข้อมูลออกนอกเครื่อง
  - อ่านไฟล์ `ActionLog` ในโฟลเดอร์เกมของเครื่องผู้เล่น ปลอดภัยจากการตรวจจับโปรแกรมช่วยเล่น (100% TOS Safe)
  - พัฒนาส่วนต่อประสานผู้ใช้ด้วย CustomTkinter ในธีมสีชมพูพาสเทลเอกลักษณ์ของทีม NEKO
  - มีโหมด Overlay หน้าต่างเล็กสำหรับเปิดลอยทับหน้าจอเกม

### Milestone 2: การปรับปรุงสู่รุ่น V6.1.0 (`26dc350`, `b9dc84f`)
* **ขอบเขต:** ปรับปรุงความเสถียรและความแม่นยำในการคำนวณรายได้ต่อชั่วโมง
* **การปรับปรุง:**
  - เพิ่มระบบตรวจจับการเข้ารหัสไฟล์ (BOM Encoding Detection): UTF-16, UTF-8-sig, UTF-8
  - เพิ่มระบบ **Watchlist Filter** ให้ผู้ใช้เลือกกรองเฉพาะไอเทมที่สนใจ
  - ปรับปรุงการจัดการไอคอนและ Taskbar Window Long Attribute บนระบบปฏิบัติการ Windows
  - โหลดและลงทะเบียนฟอนต์ภาษาไทย (Sarabun, Kanit) เข้า Windows GDI แบบ Dynamic

### Milestone 3: การเพิ่มโหมด ARKS War Room & Telemetry Sync (`cfb78eb`)
* **ขอบเขต:** เชื่อมต่อ Neko Tracker เข้ากับแคมเปญสงครามยึดพื้นที่ ARKS War Room
* **การปรับปรุง:**
  - ออกแบบสถาปัตยกรรม **EventBus** แบบ Decoupled Pub/Sub (`modules/event_bus.py`)
  - สร้างโมดูล `WarService` และหน้าจอ `WarDashboardFrame`
  - รองรับการป้อนและคัดลอกพิกัดเป้าหมาย (Coordinate Copy/Paste)
  - เพิ่มการสำรองข้อมูลสถานะออฟไลน์ลงไฟล์ `war_stats.json`
  - ปรับปรุงสีและความตัดกันของ UI (Accessibility Colors) ให้อ่านง่ายขึ้น

### Milestone 4: การอัปเกรดระบบพิกัด Sector + 4 Sub-Cells Quadrant Slots & Firebase Sync (`394ad4e`)
* **ขอบเขต:** ขยายขนาดแผนที่สงครามให้เป็นระดับกาแล็กซี และแบ่งแต่ละ Sector ออกเป็น 4 ช่องย่อย
* **การปรับปรุง:**
  - กำหนดขอบเขต Sector พิกัด X: `-12` ถึง `+25`, พิกัด Y: `-11` ถึง `+9` (รวม 798 Sectors)
  - เพิ่มระบบ **4 Quadrant Sub-cells** ต่อ Sector:
    - Slot 1: NW (บนซ้าย) — เป้าหมาย 25M N-Meseta
    - Slot 2: NE (บนขวา) — เป้าหมาย 25M N-Meseta
    - Slot 3: SW (ล่างซ้าย) — เป้าหมาย 25M N-Meseta
    - Slot 4: SE (ล่างขวา) — เป้าหมาย 25M N-Meseta
    - รวมความจุทั้ง Sector: 100M N-Meseta
  - สร้างคลาส `TargetCoord` เป็น tuple subclass รองรับการ Unpack, Indexing, และ Properties
  - เพิ่มตัวแปลงพิกัดอัจฉริยะ (Smart Coordinate Parser) รองรับ 7 รูปแบบอินพุต
  - เพิ่มเครื่องมือ `tools/firebase_war_sync.py` และ Background Worker ซิงค์สดขึ้น Firebase Realtime Database
  - **Zero-Login Architecture:** ปลดระวางระบบล็อกอินเดิมด้วยรหัสผ่าน หันมาใช้การตรวจจับชื่อตัวละครในเกมผ่านไฟล์ Log อัตโนมัติเป็น Primary Key

### Milestone 5: การสร้างต้นแบบ C# .NET 6 WPF Native Tracker (V7.0.0-alpha)
* **ขอบเขต:** พัฒนาตัวโปรแกรมเวอร์ชันเนทีฟ Windows ประสิทธิภาพสูง
* **การปรับปรุง:**
  - โครงสร้างโครงการ C# WPF แยกเป็น [`NekoTracker-WPF/`](../../NekoTracker-WPF/)
  - ระบบความปลอดภัย **AntiTamperGuard** ตรวจจับการโกงและการปลอมแปลง Process
  - ระบบ **ActionLogParser** และ **LogWatcher** แบบ Strong-typed
  - ระบบภาษาหลายภาษา **LanguageManager** (EN, JA, TH)
  - ชุดทดสอบ Unit Tests [`NekoTracker.Tests/`](../../NekoTracker.Tests/) ครอบคลุม 27 กรณีทดสอบ ผ่าน 100%

### Milestone 6: การจัดระเบียบโครงสร้างคลังและการประกาศธรรมาภิบาลเอกสาร (Repository Governance)
* **ขอบเขต:** ปรับปรุงโครงสร้างคลังโค้ดและเอกสารให้ได้มาตรฐานสากล
* **การดำเนินการ:**
  - นำมาตรฐาน **Repository Artifact Governance** มาใช้ แยก 3 ระดับ: `current/`, `reference/`, `archive/`
  - ย้ายโมดูลการพิสูจน์ตัวตนเดิมที่ไม่ใช้งานแล้วไปยัง `archive/legacy_auth/` พร้อม Deprecation Banners
  - สร้างเอกสารทางเทคนิคและคู่มือการส่งต่องาน (`ACTIVE_SPECIFICATION.md`, `ARCHITECTURE.md`, `COORDINATE_SYSTEM.md`, `FIREBASE_WIRE_SCHEMA.md`, `AI_HANDOFF.md`)
  - อัปเดต `.gitignore` ป้องกันไม่ให้ Artifact คอมไพล์ของ .NET (`bin/`, `obj/`) เข้าสู่ระบบ Version Control
  - ตรวจสอบความถูกต้องของชุดทดสอบทั้ง Python (18/18 ผ่าน) และ C# (27/27 ผ่าน) โดยไม่มีข้อผิดพลาดถดถอย

### Milestone 7: การสร้างระบบ Installer และไปป์ไลน์กระจายซอฟต์แวร์ (Automated Installer & Packaging Pipeline)
* **ขอบเขต:** สร้างชุดติดตั้ง Windows มาตรฐาน (.exe Installer) สำหรับรุ่น **V7.0.0-alpha** (WPF Native) และไปป์ไลน์คอมไพล์/ตรวจสอบความสมบูรณ์อัตโนมัติ
* **การดำเนินการ:**
  - พัฒนา Inno Setup 6 Script (`installer/NekoTracker.iss`) รองรับ 64-bit Windows พร้อม LZMA2 Solid Compression สำหรับรุ่น V7.0.0-alpha
  - ยึดตัวโปรแกรมเนทีฟ C# .NET 6 WPF (`NekoTracker.exe`) เป็นแอปพลิเคชันหลักของ V7.0.0-alpha พร้อมระบบ AntiTamperGuard และฮาร์ดแวร์เร่งความเร็ว
  - บรรจุ Companion Engine (Python Tracker V6.1.0 พร้อม ARKS War Room & Firebase Sync) ไว้ในไดเรกทอรีย่อย `python-v6/`
  - สร้างสคริปต์อัตโนมัติ `installer/build_installer.py` และ Batch Script `build_installer.bat`
  - เพิ่มขั้นตอนการตรวจสอบก่อนบิลด์ (Pre-flight Tests): 18 Python tests + 27 C# tests (รวม 45 การทดสอบ)
  - ติดตั้งและทำ Process Smoke Test ใน Sandbox อัตโนมัติ: ติดตั้งเงียบ ตรวจสอบว่า Process ทั้งสองตัวรันได้โดยไม่แคช และลบออกอย่างหมดจด
  - สร้างไฟล์อาร์ติแฟกต์ทางการ `artifacts/release-v7.0.0-alpha/NekoTracker-Setup-v7.0.0-alpha.exe` พร้อม `SHA256SUMS.txt` และเอกสารกำกับ `README.md` ตามมาตรฐาน Repository Artifact Governance

### Milestone 8: ระบบตรวจสอบความปลอดภัยของเลขเวอร์ชันและการควบคุมยอดเงินบน Firebase (Version Security & Firebase Meseta Gating)
* **ขอบเขต:** อัปเกรดเวอร์ชันระบบเป็น **7.1.0** (แก้ไขช่องโหว่ความปลอดภัยจากรุ่น `7.0.0-alpha`), ส่งเลขเวอร์ชันไคลเอนต์ (`client_version`) ขึ้น Firebase RTDB และปฏิเสธไม่นับยอดเงินเข้าฐานข้อมูลสำหรับไคลเอนต์เวอร์ชันเก่า/ไม่ปลอดภัย
* **การดำเนินการ:**
  - อัปเกรดเวอร์ชันใน C# WPF (`AppVersion.cs`, `NekoTracker.csproj`) และ Python (`config.py`) เป็น `7.1.0`
  - เพิ่มฟังก์ชัน `parse_semver`, `compare_semver`, `is_version_secure` เพื่อเปรียบเทียบ Semantic Version และตรวจสอบสิทธิ์ความปลอดภัย
  - ปรับปรุง `WarService` ให้ส่ง `client_version`, `version`, `security_status`, `version_security_valid` ในทุก Payload (`operatives`, `sectors`, `sub_cells`, `latest_telemetry`, `war_logs`)
  - ติดตั้งเกตความปลอดภัย: หากไคลเอนต์ยังใช้ `7.0.0-alpha` (หรือเวอร์ชันที่ถูกเพิกถอน) ฟิลด์ `meseta` จะถูกปรับเป็น 0 ไม่ถูกนับเข้าฐานข้อมูล และบันทึกคำเตือนความปลอดภัย
  - ปรับปรุง `tools/firebase_war_sync.py` ให้ตรวจสอบ `client_version` และตัดยอดเงินเป็น 0 สำหรับเวอร์ชันที่ไม่ปลอดภัย
  - เพิ่ม `TamperViolationType.InsecureClientVersion` ใน `AntiTamperGuard` และป้องกันไม่ให้ `TrackerStats` นับเงินเข้ากระเป๋าเมื่อเวอร์ชันไม่ปลอดภัย
  - สร้างข้อกำหนด Firebase RTDB Security Rules (`database.rules.json`) บังคับตรวจ `client_version`
  - เพิ่มชุดทดสอบครอบคลุมทั้ง Python (22 รายการ ผ่าน 100%) และ C# (39 รายการ ผ่าน 100%) รวม 61 รายการทดสอบ

### Milestone 9: การกำหนดมาตรฐานกลางระบบติดตั้งซอฟต์แวร์ Windows (NEKO FAMILY Installer Standard)
* **ขอบเขต:** จัดทำมาตรฐานกลางระบบตัวติดตั้ง Windows สำหรับคลังโค้ดในเครือ NEKO FAMILY โดยถอดแบบความสำเร็จจากสถาปัตยกรรม `Neko-Family-Proxy` และปรับแก้ตัวติดตั้งของโปรเจกต์นี้ให้ใช้โปรแกรมหลักที่ถูกต้อง
* **การดำเนินการ:**
  - สร้างเอกสารข้อกำหนดมาตรฐานกลาง [`Doc/reference/INSTALLER_STANDARD.md`](../reference/INSTALLER_STANDARD.md) และคู่มือโฟลเดอร์ [`installer/README.md`](../../installer/README.md)
  - ปรับปรุง `installer/NekoTracker.iss`:
    - ย้ายตำแหน่งติดตั้งมายัง `%LOCALAPPDATA%\NEKO FAMILY\NekoTracker` (Per-User Local AppData topology)
    - ตั้งค่า `PrivilegesRequired=lowest` เพื่อให้ติดตั้งได้ทันทีโดยไม่ต้องใช้สิทธิ์ Administrator (Zero UAC elevation)
    - กำหนด `ArchitecturesAllowed=x64compatible` บล็อกระบบที่ไม่ใช่ 64-bit อย่างเด็ดขาด
    - คืนสิทธิ์การเป็นโปรแกรมหลัก (`{app}\NekoTracker.exe`, ชอร์ตคัต Desktop และ Start Menu) ให้กับ **Python Tracker V6.1.0 (พร้อมโหมด ARKS War Room & Firebase Sync)** ตรงตามที่ผู้ใช้งานคาดหวัง 100%
    - ย้ายตัวทดลอง C# WPF ไปไว้ในโฟลเดอร์พรีวิว `{app}\wpf-preview\` พร้อมชอร์ตคัตเฉพาะทาง
  - ปรับปรุงสคริปต์ไปป์ไลน์ `installer/build_installer.py`:
    - รัน Pre-flight Test Suites ทั้งหมดก่อนเสมอ (Fail-Closed)
    - แพ็กเกจไบนารี Python ด้วย PyInstaller Onedir รวมฟอนต์, โลโก้, และโมดูลครบถ้วน
    - คอมไพล์ตัวติดตั้ง Single-EXE ด้วย Inno Setup 6 (`ISCC.exe`) และคำนวณแฮช SHA-256 สู่ `artifacts/release-v6.1.0/SHA256SUMS.txt`
    - รัน Automated Lifecycle & Process Smoke Test ทดสอบการติดตั้งเงียบใน Sandbox, รัน Process Smoke ยืนยันว่า `NekoTracker.exe` (Python Tracker) เปิดติดและทำงานได้ต่อเนื่อง ไม่แครช และทดสอบการถอนการติดตั้งอย่างหมดจด
  - บันทึกและทดสอบกระบวนการทั้งหมดผ่าน `build_installer.bat` และ `python installer/build_installer.py` สำเร็จ 100% (ไฟล์ติดตั้งขนาด ~105.40 MB)

### Milestone 10: การยกเลิกเวอร์ชัน C# WPF และรวมศูนย์การพัฒนาสู่ Python Tracker (WPF Cancellation & Python Consolidation)
* **ขอบเขต:** ยกเลิกการพัฒนาเวอร์ชัน C# .NET 6 WPF อย่างเป็นทางการ และนำโค้ดเบสทั้งหมดกลับสู่สถาปัตยกรรม Python Tracker เพียงระบบเดียวตามคำสั่งและทิศทางของผู้ใช้
* **เหตุผลการตัดสินใจ:**
  - ลดภาระในการดูแลระบบสองภาษาคู่ขนาน (Dual-stack Maintenance Overhead)
  - รวมศูนย์ฟีเจอร์ โลจิก และความสามารถทั้งหมด (UI CustomTkinter, ARKS War Room, EventBus, ระบบพิกัด Sector + 4 Slots, การส่ง Telemetry สดขึ้น Firebase RTDB, และการตรวจจับ Log แบบเรียลไทม์) ให้อยู่บน Python Tracker ซึ่งมีความคล่องตัวสูง
* **การดำเนินการ:**
  - ย้ายโครงการเนทีฟ C# WPF ทั้งหมด (`NekoTracker-WPF/` และ `NekoTracker.Tests/`) ไปยัง `archive/legacy_wpf/` ตามหลักธรรมาภิบาล พร้อมเอกสาร `archive/legacy_wpf/README.md`
  - จัดทำเอกสารข้อกำหนดอดีต `Doc/archive/WPF_NATIVE_SPEC.md` และอัปเดตสารบัญเอกสารใน `Doc/archive/README.md` และ `archive/README.md`
  - ปรับปรุงเอกสารสเปคหลัก `Doc/current/ACTIVE_SPECIFICATION.md` และคู่มือส่งต่องาน `Doc/current/AI_HANDOFF.md` ให้เป็น Pure Python Toolchain ตัด .NET 6 SDK ออก
  - ปรับปรุงไปป์ไลน์ตัวติดตั้ง `installer/build_installer.py` และ Inno Setup Script `installer/NekoTracker.iss` ให้คอมไพล์และบรรจุเฉพาะ Python Tracker แบบเดี่ยว (ไม่มี `wpf-preview`)
  - อัปเดต `tools/package_test_build.py` และสคริปต์ทดสอบให้รองรับเฉพาะโมเดล Python
  - รันการทดสอบ Python Unit & Integration Tests ยืนยันผลการทำงานผ่านครบถ้วน 24 / 24 รายการ (100% Passed)

### Milestone 11: การพอร์ตระบบความปลอดภัย AntiTamperGuard สู่ Python Tracker (Native 7-Layer Anti-Tamper & Data Integrity)
* **ขอบเขต:** พอร์ตสถาปัตยกรรมป้องกันการโกงและการแทรกแซงข้อมูล `AntiTamperGuard` จาก C# Legacy มาเป็นโมดูลเนทีฟของ Python Tracker (`modules/security/`) เพื่อปิดช่องโหว่การตัดต่อและปลอมแปลง ActionLog ภายในเครื่องอย่างสมบูรณ์
* **การดำเนินการ:**
  - สร้างโมดูลความปลอดภัยเนทีฟ `modules/security/`:
    - `tamper_violation.py`: บรรจุ `TamperViolationType` (12 ประเภทการละเมิด) และคลาส `TamperViolation`
    - `process_validator.py`: ตรวจสอบ Process `pso2.exe` ผ่าน Windows Toolhelp32Snapshot (`IProcessValidator`, `WindowsProcessValidator`, `MockProcessValidator`)
    - `action_log_record.py`: ตัวแปลง `ActionLogParser` และคลาส `ActionLogRecord`
    - `file_handle_validator.py`: ตรวจสอบการถือครอง Write Handle บนไฟล์ Log ผ่าน Windows Restart Manager API (`rstrtmgr.dll`) เพื่อยืนยันว่า `pso2.exe` เป็นผู้เปิดไฟล์จริงและตรวจจับ Concurrent Writer ผิดปกติ
    - `path_validator.py`: ตรวจสอบ Path ไดเรกทอรีทางการของ SEGA และตรวจจับการใช้ Reparse Point / NTFS Symlink ปลอมแปลง
    - `cadence_analyzer.py`: วิเคราะห์ความสม่ำเสมอทางสถิติ (Entropy & Jitter) ตรวจจับบอทที่ส่งเงินดรอปเป็นจังหวะตายตัว (StdDev < 0.05s)
    - `anti_tamper.py`: คลาสหลัก `AntiTamperGuard` รวมศูนย์การตรวจสอบ 9 เกราะป้องกันระดับสูง
  - ผสานรวมเข้ากับ `meseta_tracker.py`:
    - ตรวจสอบความต่อเนื่องของขนาดไฟล์และสถานะ File Handle ใน `monitor_log_file` ก่อนอ่าน
    - ตรวจสอบ `validate_record` พร้อมตรวจจับ Bot Cadence ใน `process_log_line` ก่อนสะสมเงิน `session_meseta` และไอเทมดรอป
    - เชื่อมโยง Event `tamper_violation` เข้ากับ `EventBus`
  - ผสานรวมเข้ากับ `WarService`:
    - ดักจับ Event `tamper_violation` และบันทึกลง `war_logs`
    - หากเกิดการละเมิดร้ายแรง ปรับ `is_tamper_compromised = True`, ปรับ `meseta = 0`, สแตมป์สถานะ `"TAMPER_COMPROMISED"`, และตัดสิทธิ์การซิงค์ขึ้น Firebase RTDB
  - เพิ่มชุดทดสอบเฉพาะทาง `tests/test_anti_tamper.py` (16 รายการทดสอบ)
  - รันการทดสอบ Unit Tests ทั้งหมดในคลังโค้ดผ่านสมบูรณ์ 100% (40 / 40 รายการทดสอบ)

### Milestone 12: ระบบวิธีใช้งานแบบ 3 ภาษา (TH/EN/JA) พร้อมลิงก์ Discord และเครดิตชุมชนทางการ
* **ขอบเขต:** พัฒนาระบบคู่มือแนะนำการใช้งาน (How-To-Use Guide) แบบอินเทอร์แอคทีฟ รองรับ 3 ภาษา (ไทย, English, 日本語) ภายในแอปพลิเคชัน พร้อมจัดทำเอกสารคู่มือฉบับสมบูรณ์ และระบุเครดิตชุมชนทางการ `NEKO★FAMILY PSO2:NGS Community discord.gg/fkjXW9AJ6a`
* **การดำเนินการ:**
  - สร้างโมดูล `modules/guide_dialog.py`:
    - หน้าต่าง Dialog แบบโมเดิร์น สไตล์คลีน พร้อม Pink Header Bar และ Close Button
    - รองรับการสลับภาษาแบบสด (In-flight Language Switcher: `[EN | TH | JA]`) ซิงค์กับระบบหลักของแอป
    - ระบบแท็บ 5 หมวดหมู่หลัก:
      1. `🚀 Setup & Logs`: ขั้นตอนการเลือกโฟลเดอร์ Log, Zero-Login, 100% TOS Safe
      2. `💰 Meseta & Items`: การคำนวณเงิน, อัตรา M/hr, First-drop Timer, Item Watchlist Filter, Reset
      3. `🪟 Gadget Overlay`: การใช้งาน Full Overlay และ Mini Overlay, Drag & Move
      4. `⚔️ ARKS War`: การเข้าร่วมสงคราม, พิกัด Sector & 4 Slots (10M/40M V9), Smart Paste, Cloud Sync, Web Map
      5. `🌸 Community & Credit`: กล่อง Discord คอมมูนิตี้, ปุ่ม Join Discord, ปุ่ม Copy Link (พร้อม Toast แจ้งเตือน), และเครดิตทางการ
  - ผสานรวมเข้ากับ UI ของระบบ:
    - เพิ่มปุ่ม `📖 วิธีใช้งาน` (`btn_how_to_use`) ใน Sidebar ของ Main Dashboard (`meseta_tracker.py`)
    - เพิ่มปุ่ม `📖 วิธีใช้งาน` (`btn_how_to_use`) ใน Sidebar ของ ARKS War View (`modules/war_mode/war_view.py`)
    - รองรับการ Retranslate แบบไดนามิกทันทีเมื่อผู้ใช้เปลี่ยนภาษาในจุดใดก็ตาม
  - ขยายระบบคำศัพท์ `modules/i18n.py`:
    - เพิ่มคีย์แปลภาษาสำหรับ Guide Window และปุ่มทั้งหมดครบถ้วนทั้ง 3 ภาษา (EN, TH, JA)
  - จัดทำเอกสารคู่มือทางการ:
    - สร้าง `Doc/current/HOW_TO_USE.md` บรรจุเนื้อหาคู่มือละเอียดครบ 3 ภาษา
    - อัปเดต `Doc/current/ACTIVE_SPECIFICATION.md` และ `README.md`
  - เพิ่มชุดทดสอบเฉพาะทาง `tests/test_guide_system.py` (7 รายการทดสอบ):
    - ตรวจสอบความครบถ้วนของข้อมูล 3 ภาษา, การสลับภาษาแบบสด, Single-instance Lifecycle, การคัดลอกลิงก์, การเปิด Discord, และการปฏิบัติตามข้อกำหนด Coordinate War Engine V9
  - รันการทดสอบทั้งหมดผ่านครบถ้วน 57 / 57 รายการ (100% Passed)

### Milestone 13: การปกป้องข้อมูลความลับและสถาปัตยกรรมหลังบ้านบนส่วนผลิตภัณฑ์ (Product Data & Backend Sanitization)
* **ขอบเขต:** ตรวจสอบและกำจัดข้อมูลความลับ, รายละเอียดเทคโนโลยีหลังบ้าน (Backend Infrastructure), กฎฐานข้อมูล, และพาธภายในเครื่องพัฒนา ออกจากหน้าจอผู้ใช้และอาร์ติแฟกต์สำหรับแจกจ่ายผู้ใช้ (Sanitization & Defense-in-Depth)
* **การดำเนินการ:**
  - **กำจัดกฎฐานข้อมูลจากชุดทดสอบสำหรับผู้ใช้:**
    - ลบไฟล์ `database.rules.json` ออกจาก `artifacts/portable-test-v7.1.0/`
    - ปรับปรุง `tools/package_test_build.py` ไม่ให้คัดลอก `database.rules.json` เข้าสู่ชุดแจกจ่าย และตัด `--collect-all tools` เพื่อไม่ให้แพ็กเกจสคริปต์การบิลด์และบรอดคาสเตอร์ภายในลงในไดเรกทอรีแอปพลิเคชัน
  - **ซ่อนชื่อผู้ให้บริการและเทคโนโลยีหลังบ้านบนหน้าจอผู้ใช้ (UI & Dialogs):**
    - ปรับปรุง `modules/i18n.py`: ปรับข้อความสถานะ `war_syncing`, `war_synced`, `msg_anti_tamper_compromised`, `msg_security_revoked` ในทั้ง 3 ภาษา (EN, TH, JA) ให้ใช้คำว่า `Cloud Sync` / `ระบบซิงค์ออนไลน์` / `クラウド同期` แทนการระบุชื่อเทคโนโลยีหลังบ้าน
    - ปรับปรุง `modules/guide_dialog.py`: แก้ไขการ์ดที่ 3 ของแท็บ ARKS War ทั้ง 3 ภาษา ไม่เปิดเผยชื่อผู้ให้บริการคลาวด์และโครงสร้างหลังบ้าน
    - ปรับปรุง `modules/war_mode/war_service.py`: ปรับข้อความตอบกลับสถานะการซิงค์ให้เป็นข้อความกลาง ป้องกันการหลุดของ Exception URL และชื่อระบบฐานข้อมูล
  - **ลบพาธดิสก์และข้อความสถาปัตยกรรมภายในออกจากเอกสาร:**
    - ลบพาธไดรฟ์พัฒนาภายใน (`E:\...`) ออกจาก `README.md`, `config.py`, `Doc/current/ACTIVE_SPECIFICATION.md`, `Doc/current/AI_HANDOFF.md`, `Doc/reference/COORDINATE_SYSTEM.md`, และ `tests/test_guide_system.py`
    - ปรับปรุง `Doc/reference/FIREBASE_WIRE_SCHEMA.md` กำหนด URL ผ่าน Environment Variable (Private Endpoint)
    - ปรับปรุง `Doc/current/HOW_TO_USE.md`, `artifacts/portable-test-v7.1.0/HOW_TO_USE.md`, `คู่มือการทดสอบ_README.txt`, และ `README_TEST_GUIDE.md` ให้เป็นคำอธิบายกลาง (Cloud Realtime Sync)
  - **คอมไพล์และประกอบชุด Portable Test Package ใหม่:**
    - รัน `tools/package_test_build.py --rebuild` ประกอบไบนารีและสร้างแพ็กเกจ `portable-test-v7.1.0` และ `NekoTracker-v7.1.0-Portable-Test.zip` พร้อมคำนวณ `SHA256SUMS.txt` ใหม่
  - **การทดสอบความถูกต้อง:**
    - รันชุดทดสอบทั้งหมด 57 / 57 ผ่าน 100% (Green)

### Milestone 14: การทดสอบ End-to-End (E2E) ครบวงจรและการตรวจสอบความพร้อมรอบสุดท้ายก่อน Release (Final Pre-Release E2E Verification & Pipeline Gate)
* **ขอบเขต:** ดำเนินการทดสอบ End-to-End (E2E) เต็มรูปแบบตลอดวงจรการทำงานของผู้ใช้, ปิดช่องว่างการทดสอบของระบบแปลภาษา, ประกอบและทดสอบกระบวนการบิลด์ตัวติดตั้ง (Installer Pipeline) และชุดทดสอบพกพา (Portable Test Package) พร้อมตรวจสอบ Process Smoke ก่อนการ Release อย่างเป็นทางการ
* **การดำเนินการ:**
  - **สร้างชุดทดสอบ End-to-End Lifecycle (`tests/test_e2e_lifecycle.py`):**
    - ทดสอบการอ่านและประมวลผลไฟล์สตรีมมิ่งสดผ่าน `MockLogSimulator`
    - ตรวจสอบความถูกต้องของการคำนวณ N-Meseta, กระเป๋าเงิน, อัตราความเร็ว M/hr, และการสะสมรายการไอเท็มดรอป
    - ทดสอบระบบกรองไอเท็มเฉพาะ Watch List (เปิด/ปิด Filter)
    - ทดสอบวงจรชีวิตของหน้าต่าง Overlay ทั้งโหมด Mini และ Full
    - ทดสอบ ARKS War Room: เลือกพิกัดจาก Landmark Preset ("Core" [0, 0]), บันทึกพิกัดด้วยตนเอง, และยิง Cloud Telemetry ซิงค์ออนไลน์
    - ทดสอบการสลับภาษาแบบสดระหว่างใช้งาน (In-flight Language Switching: EN ↔ TH ↔ JA)
    - ทดสอบหน้าต่างคู่มือ (GuideWindow): การเปิดหน้าต่าง, การเปลี่ยนแท็บครบทั้ง 5 แท็บ, ลิงก์ Discord ชุมชน และการปิดหน้าต่างอย่างสมบูรณ์
    - ทดสอบการล้างค่าข้อมูลรอบการเล่น (Session Reset) และการป้องกันการปลอมแปลงข้อมูล (Anti-Tamper Rejection)
  - **ปรับแต่งชุดทดสอบ i18n (`tests/test_i18n.py`):**
    - ปรับปรุงข้อความทดสอบภาษาไทยให้ตรงกับศัพท์ทางการชุดใหม่ (Professional Tone) จากคอมมิตล่าสุด
  - **ปรับปรุงสคริปต์ตัวสร้างแพ็กเกจพกพา (`tools/package_test_build.py`):**
    - เพิ่มค่าตัวแปรสิ่งแวดล้อมและพารามิเตอร์ `--test` ในสคริปต์ Batch เพื่อให้รันในโหมดทดสอบได้อย่างราบรื่น
  - **การรันชุดทดสอบระบบ:**
    - รันการทดสอบ Unit, Integration และ E2E ผ่านทั้งหมด **64 / 64 รายการ (100% Passed)**
  - **การบิลด์และทดสอบตัวติดตั้งทางการ (Installer & Smoke Gate):**
    - คอมไพล์ไบนารี PyInstaller และ Inno Setup 6 ได้ไฟล์ `artifacts/release-v7.1.0/NekoTracker-Setup-v7.1.0.exe` (ขนาด 22.18 MB)
    - คำนวณ SHA-256: `f11264c7ff9d51b0541ba28ad78e25fb317a54e2adef0c5067a9ebe916d6c5e5`
    - ผ่านการทดสอบ Installer Lifecycle & Process Smoke Test ในสภาพแวดล้อม Sandbox
  - **การประกอบชุดทดสอบพกพา (Portable Test Package):**
    - บิลด์แพ็กเกจ `artifacts/portable-test-v7.1.0/` และ `artifacts/NekoTracker-v7.1.0-Portable-Test.zip` (ขนาด 30.28 MB)
    - คำนวณ SHA-256: `5c29efe57efca3b0b229e2475450fbac5ffe3bc6c7d59a8ec92578587eaa1c97`
    - ทดสอบ Process Smoke ของไฟล์ไบนารีพกพาผ่านสมบูรณ์

### Milestone 15: แก้ไขบัคแถบสถานะและปุ่มเลือกไฟล์ Log ตกขอบ/หายไปในโหมด ARKS War Room & Offline (Log File Status & Folder Selector Layout Fix)
* **ปัญหาที่พบ:**
  - ผู้ใช้รายงานว่า "บัคไฟล์ log หาย" โดยในหน้าจอ ARKS War Room (และโหมด Offline) แถบแสดงสถานะไฟล์ Log (`lbl_file_status`) และปุ่มเลือกโฟลเดอร์ Log (`btn_select`) ถูกดันจนตกขอบล่างของกล่องเมนู เหลือเพียงเส้นสีแดงขอบบน 2 พิกเซล และปุ่ม "เลือกโฟลเดอร์ Log" หลุดหายไปจากหน้าจอทั้งหมด ทำให้ผู้ใช้ไม่ทราบว่าโปรแกรมอ่านไฟล์ใดอยู่ และไม่สามารถกดเลือกโฟลเดอร์ Log ได้
* **สาเหตุรากเหง้า (Root Cause):**
  - ใน `modules/war_mode/war_view.py` (`_build_menu_panel`) และ `meseta_tracker.py` มีการแพ็กวิดเจ็ตส่วนหัว (`brand_frame`) และปุ่มต่างๆ (`btn_frame`) ด้วย `side="top"` และ `expand=True` ก่อน แล้วจึงแพ็ก `status_frame` ด้วย `side="bottom"` ในลำดับหลังสุด ทำให้ Tkinter จัดสรรพื้นที่ความสูงให้ส่วนบนจนหมด เหลือพื้นที่ส่วนล่างให้ `status_frame` เพียง 0-3 พิกเซล วิดเจ็ตจึงไม่ถูก map แสดงผล
  - ฟังก์ชันตรวจหาตำแหน่งโฟลเดอร์ Log อัตโนมัติ (`Documents\SEGA\PHANTASYSTARONLINE2\log_ngs`) ค้นหาเพียงพาธเดียว ไม่ครอบคลุมกรณีติดตั้งเกมเซิร์ฟเวอร์ Global (NA) หรือโฟลเดอร์ `log` มาตรฐาน และไม่ได้บันทึกลงไฟล์คอนฟิกเมื่อตรวจพบอัตโนมัติ
* **การแก้ไข:**
  - สลับลำดับการแพ็กให้ `status_frame` และปุ่ม `btn_select` ถูกแพ็กด้วย `side="bottom"` เป็นลำดับแรก เพื่อการันตีพื้นที่แสดงผล 100% ไม่ถูกดันตกขอบ
  - ปรับขนาดและสัดส่วนกราฟิกใน `card_menu` ให้กระชับขึ้น: ปรับขนาดโลโก้เป็น 110px, รวมปุ่ม `btn_how_to_use` และ `btn_discord` เป็นแถวคู่ 2 คอลัมน์ (`row_help`), ปรับความสูงหน้าต่างหลักเป็น `950x640` เพื่อให้มีระยะปลอดภัย (Safety Margin) รองรับ Display Scaling บน Windows ทุกระดับ
  - ปรับปรุง `_find_default_pso2_log_folder()` ให้สแกนหาโฟลเดอร์ Log ของเกม PSO2:NGS ครอบคลุมทั้ง JP และ NA/Global พร้อมบันทึกลงคอนฟิกอัตโนมัติ
  - เพิ่มชุดทดสอบถดถอย `test_sidebar_and_war_view_status_frame_not_clipped` ใน `tests/test_tracker_modules.py` ครอบคลุมทั้งสองโหมด
  - รันการทดสอบ Unit Tests ทั้งหมดผ่านครบถ้วน **65 / 65 รายการ (100% Passed)**

