# 🌸 NEKO Item & Meseta Tracker (PSO2:NGS)

![Version](https://img.shields.io/badge/Python_Version-7.1.0-FF69B4?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows_10%2F11-blue?style=for-the-badge)
![Tests](https://img.shields.io/badge/Tests-56%20Passed-brightgreen?style=for-the-badge)
![Languages](https://img.shields.io/badge/i18n-EN%20%7C%20TH%20%7C%20JA-purple?style=for-the-badge)
![License](https://img.shields.io/badge/License-Non--Commercial-red?style=for-the-badge)

โปรแกรมและเครื่องมือติดตามรายได้ N-Meseta และไอเทมดรอปแบบ Real-time สำหรับเกม **Phantasy Star Online 2: New Genesis (PSO2:NGS)** พัฒนาขึ้นโดยทีม **NEKO FAMILY TEAM SHIP 4 JP** ออกแบบมาเป็นพิเศษสำหรับการฟาร์ม PSE Burst, การคำนวณอัตราความเร็ว Meseta ต่อชั่วโมง (M/hr), การทำสงครามยึดพื้นที่ในโหมด **ARKS War Room**, พร้อมระบบคู่มือวิธีใช้งานแบบไดนามิก 3 ภาษา (ไทย, English, 日本語) และการเชื่อมต่อคอมมูนิตี้ Discord ทางการ

> 🌸 **Official Community Discord & Credit:**  
> **NEKO★FAMILY PSO2:NGS Community discord.gg/fkjXW9AJ6a**  
> 🔗 Discord: [https://discord.gg/fkjXW9AJ6a](https://discord.gg/fkjXW9AJ6a)  
> 📖 คู่มือการใช้งาน 3 ภาษา: [`Doc/current/HOW_TO_USE.md`](Doc/current/HOW_TO_USE.md)

---

## 🏛️ ผังโครงสร้างโฟลเดอร์และการกำกับดูแล (Repository Directory Tree)

คลังโค้ดนี้ได้รับการจัดระเบียบตามมาตรฐาน **Repository Artifact Governance** แบ่งระดับสิทธิ์และสถานะการใช้งานอย่างชัดเจน:

```
E:\PSO2NGS-NEKO-Item-Meseta-tracker\
├── 📂 Doc/                                 # [REFERENCE] ศูนย์รวมเอกสารระบบและธรรมาภิบาล
│   ├── README.md                           # สารบัญเอกสารหลักและ Governance Matrix
│   ├── 📂 current/                         # [CURRENT] 🟢 เอกสารสเปคและคู่มือที่ใช้งานจริง
│   │   ├── ACTIVE_SPECIFICATION.md         # ข้อกำหนดทางเทคนิคฉบับสมบูรณ์ (V6.1 & V7.0)
│   │   ├── ENGINEERING_LOG.md              # บันทึกประวัติวิศวกรรมและวิวัฒนาการระบบ
│   │   └── AI_HANDOFF.md                   # คู่มือส่งต่องานสำหรับ AI Agents และวิศวกร
│   ├── 📂 reference/                       # [REFERENCE] 🔵 เอกสารอ้างอิงเชิงลึก
│   │   ├── ARCHITECTURE.md                 # ผังสถาปัตยกรรมระบบและท่อส่งข้อมูล (Data Pipelines)
│   │   ├── COORDINATE_SYSTEM.md            # ข้อกำหนดระบบพิกัด Sector + 4 Sub-cell Slots
│   │   ├── FIREBASE_WIRE_SCHEMA.md         # เอกสารข้อกำหนดสถาปัตยกรรมและการเชื่อมต่อข้อมูล
│   │   └── SECURITY_ANTITAMPER.md          # มาตรฐาน 100% TOS Safe และ AntiTamperGuard
│   └── 📂 archive/                         # [ARCHIVE] 🔴 ข้อกำหนดที่ปลดระวางแล้ว
│       ├── README.md                       # สารบัญเอกสารเก่าที่ปลดระวาง
│       ├── LEGACY_LOGIN_SPEC.md            # ระบบ Login เดิมที่ถูกยกเลิก (แทนที่ด้วย Zero-Login)
│       └── V6_OFFLINE_TRACKER_SPEC.md      # สเปคเดิมก่อนมีระบบ ARKS War Room
├── 📂 modules/                             # [CURRENT] 🟢 โมดูลระบบ Python ย่อย
│   ├── __init__.py                         # Package Entrypoint
│   ├── event_bus.py                        # ตัวกระจายเหตุการณ์ Decoupled EventBus
│   └── 📂 war_mode/                        # โหมดสงคราม ARKS War Room
│       ├── __init__.py                     # War Subsystem Package
│       ├── war_service.py                  # Service จัดการ Telemetry และพิกัด TargetCoord
│       └── war_view.py                     # แดชบอร์ดสงคราม ARKS WarDashboardFrame
├── 📂 tools/                               # [CURRENT] 🟢 สคริปต์และเครื่องมือเสริม
│   ├── __init__.py                         # Tools Package
│   └── firebase_war_sync.py                # เครื่องมือส่งข้อมูล Telemetry สด (Admin SDK + REST)
├── 📂 tests/                               # [CURRENT] 🟢 ชุดทดสอบ Unit Tests ของ Python
│   └── test_tracker_modules.py             # ทดสอบ EventBus, WarService, Zero-Login, SemVer, Security (24 Tests)
├── 📂 installer/                           # [CURRENT] 🟢 ไฟล์กำหนดค่าและสคริปต์ไปป์ไลน์ตัวติดตั้ง
│   ├── NekoTracker.iss                     # สคริปต์ Inno Setup 6 (Per-user, 64-bit, LZMA2 Compression)
│   ├── build_installer.py                  # สคริปต์อัตโนมัติ (Tests -> Builds -> Package -> Smoke)
│   ├── LICENSE.txt                         # ข้อกำหนดและสิทธิ์การใช้งาน (Non-Commercial)
│   └── README.md                           # คู่มือการทำงานของระบบตัวติดตั้ง
├── 📂 artifacts/                           # [CURRENT] 🟢 คลังอาร์ติแฟกต์ทางการ
│   └── 📂 release-v6.1.0/                  # [CURRENT] 🟢 โฟลเดอร์ Release หลัก (Python Tracker Setup.exe, SHA256, Docs)
├── 📂 archive/                             # [ARCHIVE] 🔴 ซอร์สโค้ดเก่าที่ปลดระวาง (ห้ามใช้งาน)
│   ├── README.md                           # บันทึกชี้แจงเหตุผลการปลดระวางโค้ด
│   ├── 📂 legacy_auth/                     # โค้ดระบบ Login เก่าที่ยกเลิกไปแล้ว
│   └── 📂 legacy_wpf/                      # โครงการ C# WPF Native Tracker ที่ยกเลิกการพัฒนาแล้ว
├── 📂 fonts/                               # ฟอนต์ Sarabun และ Kanit สำหรับ Windows GDI
├── config.py                               # ค่าคอนฟิกูเรชันหลักของ Python App
├── dashboard_ui.py                         # แดชบอร์ดสรุปสถิติหน้าแรก
├── overlay_ui.py                           # หน้าต่าง Transparent Overlay (Full / Mini)
├── meseta_tracker.py                       # จุดเริ่มต้นรันหลักของ Python Application
├── run_app.bat                             # สคริปต์เปิดรันแอปพลิเคชันอย่างรวดเร็ว
├── run_test.bat                            # สคริปต์รันชุดทดสอบ Python อัตโนมัติ
├── build_installer.bat                     # สคริปต์สร้างไฟล์ติดตั้ง Windows Setup อัตโนมัติ
└── README.md                               # เอกสารหลักฉบับนี้
```

---

## ✨ คุณสมบัติเด่นของระบบ (Core Features)

### 1. ⚡ Real-time Tracking & 100% TOS Safe
* **คำนวณเงินสดทันใจ:** ติดตามการได้รับ N-Meseta และคำนวณอัตราความเร็ว Meseta ต่อชั่วโมง (M/hr) อัตโนมัติ
* **ปลอดภัยจากการแบน 100%:** อ่านข้อมูลผ่านไฟล์ข้อความ `ActionLog` ที่ตัวเกม PSO2:NGS สร้างขึ้นในเครื่องเท่านั้น ไม่มีการอ่าน Memory ไม่มีการดัดแปลงไฟล์เกม ไม่มีการฉีด DLL (Zero Injection)
* **Item Watchlist Filter:** กรองติดตามเฉพาะไอเทมหายาก แคปซูลพิเศษ หรืออาวุธที่ต้องการได้ตามใจชอบ
* **Gadget Mode (Overlay):** หน้าต่างมินิมอลโปร่งใส เปิดลอยทับหน้าจอเกมโดยไม่เกะกะ มีทั้งโหมด Full และ Mini Meseta

### 2. ⚔️ ARKS War Room & ระบบพิกัด Sector + 4 Slots (Coordinate War V9)
* **ปรัชญาหลัก:** **"เกมแค่เติมเงินเข้าไปในช่อง ใครใส่เยอะคนนั้นเป็นเจ้าของ"** (อ้างอิง Coordinate War Specification V9)
* **ตารางพิกัดระดับกาแล็กซี:** ครอบคลุม Sector X: `[-12 .. +25]` และ Sector Y: `[-11 .. +9]` รวมทั้งสิ้น 798 Sectors
* **4 Quadrant Sub-cell Slots:** แบ่งแต่ละ Sector ออกเป็น 4 ช่องย่อย (ขนาดช่องละ 300px x 300px):
  - ช่อง `#1` (NW บนซ้าย) — เกณฑ์ปลดล็อกยึดครอง 10,000,000 N-Meseta (10M ℳ)
  - ช่อง `#2` (NE บนขวา) — เกณฑ์ปลดล็อกยึดครอง 10,000,000 N-Meseta (10M ℳ)
  - ช่อง `#3` (SW ล่างซ้าย) — เกณฑ์ปลดล็อกยึดครอง 10,000,000 N-Meseta (10M ℳ)
  - ช่อง `#4` (SE ล่างขวา) — เกณฑ์ปลดล็อกยึดครอง 10,000,000 N-Meseta (10M ℳ)
  - ปลดแอกสมบูรณ์ทั้ง Sector เท่ากับ **40,000,000 N-Meseta** (หากยึดครบคนเดียวจะหลอมรวมเป็น Seamless Continent)
* **การชิงพื้นที่ (Clash):** ใครเติมเงินเกิน 10M และมากกว่าผู้นำเดิม แย่งเป็นเจ้าของทันที!
* **Smart Coordinate Parser:** วางพิกัดได้ทันที รองรับ 7 รูปแบบอินพุต (ทั้งแบบ 3 จำนวน, วงเล็บ, JSON, และข้อความคัดลอกจากเว็บ)
* **Zero-Login Architecture & Standby Presence:** ตรวจจับชื่อตัวละครจริงในเกมจากไฟล์ Log อัตโนมัติและปรากฏในทำเนียบนักรบพร้อมรบทันที
* **Cloud Realtime Sync:** เธรดเบื้องหลังส่ง Telemetry สดขึ้นระบบคลาวด์ War Room อัตโนมัติด้วย Debounce 0.35 วินาที พร้อม Heartbeat ทุก 5 วินาที

### 3. 🛡️ Client Version Security & Data Gating
* **ระบบตรวจสอบความปลอดภัยของเวอร์ชัน:** ส่งเลขเวอร์ชันไคลเอนต์ (`client_version`) ขึ้นตรวจสอบกับระบบคลาวด์อัตโนมัติทุกครั้งที่ซิงค์ข้อมูล
* **Meseta Security Gating:** ไคลเอนต์เวอร์ชันที่มีช่องโหว่ความปลอดภัยหรือถูกเพิกถอน (Revoked) จะถูกปฏิเสธไม่นับยอดเงินเข้าสู่ฐานข้อมูล (`meseta = 0`) และบันทึกคำเตือนความปลอดภัย
* **Pure Python Architecture:** ออกแบบด้วย Python 3.11 และ CustomTkinter น้ำหนักเบา ปลอดภัย และเสถียร

---

## 🚀 วิธีการใช้งาน (Getting Started)

### การติดตั้งและใช้งานสำหรับผู้เล่นทั่วไป
1. ดาวน์โหลดตัวติดตั้ง **`NekoTracker-Setup-v6.1.0.exe`** จากโฟลเดอร์ [`artifacts/release-v6.1.0/`](artifacts/release-v6.1.0/)
2. ดับเบิลคลิกติดตั้งตามวิซาร์ด (ระบบจะสร้างไอคอนทางลัดบน Desktop และ Start Menu ให้โดยอัตโนมัติ ติดตั้งในระดับผู้ใช้ ไม่ต้องใช้สิทธิ์ Admin)
3. เปิดโปรแกรม แล้วคลิกปุ่ม **"📂 จิ้มเลือกโฟลเดอร์ Log"** เลือกโฟลเดอร์ Log ของเกม PSO2:NGS
   * *พาธเริ่มต้น: `Documents\SEGA\PHANTASYSTARONLINE2\log_ngs`*
4. เริ่มต้นฟาร์มในเกม ตัวเลขเงินและรายการไอเทมจะอัปเดตแบบเรียลไทม์ทันที!
5. หากต้องการร่วมสงคราม ให้คลิก **"⚔️ เข้าสู่สงคราม (ARKS War)"** ป้อนพิกัด Sector หรือเลือกช่อง Quadrant ที่ต้องการช่วยทีมยึดครอง

### การรันจาก Source Code
* ดับเบิลคลิก `run_app.bat` หรือสั่งรัน `python meseta_tracker.py`

---

## 🏗️ การสร้างไฟล์ติดตั้ง (Installer Build Pipeline)

วิศวกรหรือผู้พัฒนาสามารถสั่งบิลด์ตัวติดตั้ง Windows พร้อมขั้นตอนการทดสอบ Process Smoke แบบอัตโนมัติ 100%:

```bash
# รันผ่าน Batch Script (คลิกเดียว)
build_installer.bat

# หรือรันผ่านคำสั่ง Python
python installer/build_installer.py
```
> ระบบจะรันการทดสอบ Python (24 รายการ ผ่าน 100%) -> แพ็กเกจ Python Tracker ด้วย PyInstaller -> คอมไพล์ Inno Setup (มาตรฐาน Per-User `%LOCALAPPDATA%\NEKO FAMILY\NekoTracker`) -> สร้างแฮช SHA-256 -> ทำ Lifecycle Smoke Test ใน Sandbox ตามมาตรฐานกลาง [`Doc/reference/INSTALLER_STANDARD.md`](Doc/reference/INSTALLER_STANDARD.md)

---

## 🧪 การรันชุดทดสอบ (Automated Testing)

โครงการนี้มีชุดทดสอบ Python Unit & Integration Tests ครอบคลุม **24 การทดสอบ** ซึ่งผ่านการรับรอง 100%:

```bash
# ทดสอบระบบ Python (24 รายการ)
python -m pytest -v

# หรือดับเบิลคลิก run_test.bat
```

---

## 📚 เอกสารประกอบโครงการ (Project Documentation)

* 📖 **[คู่มือการใช้งาน 3 ภาษา (HOW_TO_USE.md)](Doc/current/HOW_TO_USE.md)**
* 📖 **[สารบัญและหลักธรรมาภิบาลเอกสาร (Doc/README.md)](Doc/README.md)**
* 🟢 **[สเปคระบบปัจจุบัน (ACTIVE_SPECIFICATION.md)](Doc/current/ACTIVE_SPECIFICATION.md)**
* 🟢 **[บันทึกประวัติวิศวกรรม (ENGINEERING_LOG.md)](Doc/current/ENGINEERING_LOG.md)**
* 🟢 **[คู่มือส่งต่องานสำหรับ AI Agents (AI_HANDOFF.md)](Doc/current/AI_HANDOFF.md)**
* 🔵 **[มาตรฐานกลางระบบติดตั้งซอฟต์แวร์ Windows (INSTALLER_STANDARD.md)](Doc/reference/INSTALLER_STANDARD.md)**
* 🔵 **[สถาปัตยกรรมระบบและการไหลของข้อมูล (ARCHITECTURE.md)](Doc/reference/ARCHITECTURE.md)**
* 🔵 **[ข้อกำหนดระบบพิกัด Sector และ 4 Slots (COORDINATE_SYSTEM.md)](Doc/reference/COORDINATE_SYSTEM.md)**
* 🔵 **[ข้อกำหนดสถาปัตยกรรมและการเชื่อมต่อ (FIREBASE_WIRE_SCHEMA.md)](Doc/reference/FIREBASE_WIRE_SCHEMA.md)**
* 🔵 **[มาตรฐานความปลอดภัยและ AntiTamperGuard (SECURITY_ANTITAMPER.md)](Doc/reference/SECURITY_ANTITAMPER.md)**
* 🔴 **[คลังเอกสารและซอร์สโค้ดที่ปลดระวาง (Doc/archive/README.md)](Doc/archive/README.md)**

---

## 📜 Credits & License
* **Project Owner:** NEKO FAMILY TEAM SHIP 4 JP
* **Developer:** Vale3neko

### ⚠️ Terms of Use (เงื่อนไขการใช้งาน)
**[EN]** This program is created for the public benefit of the PSO2:NGS community. It is open for anyone to fork, modify, and develop further freely. However, **STRICTLY NO COMMERCIAL USE IS ALLOWED.** Do not sell, monetize, or use this software for any personal financial gain.

**[TH]** โปรแกรมนี้จัดทำขึ้นเพื่อประโยชน์สาธารณะแก่คอมมูนิตี้ผู้เล่น PSO2:NGS ผู้ใช้สามารถนำซอร์สโค้ดไปศึกษาหรือพัฒนาต่อยอดได้อย่างอิสระโดยไม่มีค่าใช้จ่าย **แต่ไม่อนุญาตให้นำไปใช้ในเชิงพาณิชย์ แสวงหาผลกำไร หรือนำไปขายต่อโดยเด็ดขาด**
