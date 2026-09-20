# 🌸 NEKO Item & Meseta Tracker (PSO2:NGS)

![Version](https://img.shields.io/badge/Python_Version-6.1.0-FF69B4?style=for-the-badge)
![WPF Version](https://img.shields.io/badge/.NET_WPF_Version-7.0.0--alpha-8A2BE2?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows_10%2F11-blue?style=for-the-badge)
![Tests](https://img.shields.io/badge/Tests-40%20Passed-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/License-Non--Commercial-red?style=for-the-badge)

โปรแกรมและเครื่องมือติดตามรายได้ N-Meseta และไอเทมดรอปแบบ Real-time สำหรับเกม **Phantasy Star Online 2: New Genesis (PSO2:NGS)** พัฒนาขึ้นโดยทีม **NEKO FAMILY TEAM SHIP 4 JP** ออกแบบมาเป็นพิเศษสำหรับการฟาร์ม PSE Burst, การคำนวณอัตราความเร็ว Meseta ต่อชั่วโมง (M/hr), และการทำสงครามยึดพื้นที่ในโหมด **ARKS War Room**

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
│   │   ├── FIREBASE_WIRE_SCHEMA.md         # Wire Contract ของ Google Firebase RTDB
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
│   └── firebase_war_sync.py                # ตัวส่งข้อมูลขึ้น Firebase RTDB (Admin SDK + REST)
├── 📂 tests/                               # [CURRENT] 🟢 ชุดทดสอบ Unit Tests ของ Python
│   └── test_tracker_modules.py             # ทดสอบ EventBus, WarService, Zero-Login (13 Tests)
├── 📂 NekoTracker-WPF/                     # [CURRENT] 🟢 โครงการเนทีฟ C# .NET 6 WPF (V7.0.0-alpha)
│   ├── App.xaml / App.xaml.cs              # จุดเริ่มต้นโปรแกรม WPF
│   ├── MainWindow.xaml / cs                # หน้าต่างหลักธีมพาสเทล
│   ├── OverlayWindow.xaml / cs             # หน้าต่าง Overlay ลอยทับเกม
│   ├── 📂 Core/                            # ActionLogParser, LogWatcher, TrackerStats
│   ├── 📂 Security/                        # AntiTamperGuard, IProcessValidator
│   ├── 📂 Localization/                    # LanguageManager (en, ja, th)
│   └── 📂 Themes/                          # PastelTheme.xaml
├── 📂 NekoTracker.Tests/                   # [CURRENT] 🟢 ชุดทดสอบ Unit Tests ของ C# WPF
│   ├── AntiTamperTests.cs                  # ทดสอบระบบตรวจจับการโกงและการปลอมแปลง
│   ├── LocalizationTests.cs                # ทดสอบการแปลภาษาแบบ JSON
│   ├── LogParserTests.cs                   # ทดสอบการ Parse ข้อความ ActionLog
│   └── VersioningTests.cs                  # ทดสอบการกำหนดเวอร์ชัน V7
├── 📂 archive/                             # [ARCHIVE] 🔴 ซอร์สโค้ดเก่าที่ปลดระวาง (ห้ามใช้งาน)
│   ├── README.md                           # บันทึกชี้แจงเหตุผลการปลดระวางโค้ด
│   └── 📂 legacy_auth/                     # โค้ดระบบ Login เก่าที่ยกเลิกไปแล้ว
├── 📂 fonts/                               # ฟอนต์ Sarabun และ Kanit สำหรับ Windows GDI
├── config.py                               # ค่าคอนฟิกูเรชันหลักของ Python App
├── dashboard_ui.py                         # แดชบอร์ดสรุปสถิติหน้าแรก
├── overlay_ui.py                           # หน้าต่าง Transparent Overlay (Full / Mini)
├── meseta_tracker.py                       # จุดเริ่มต้นรันหลักของ Python Application
├── run_app.bat                             # สคริปต์เปิดรันแอปพลิเคชันอย่างรวดเร็ว
├── run_test.bat                            # สคริปต์รันชุดทดสอบ Python อัตโนมัติ
└── README.md                               # เอกสารหลักฉบับนี้
```

---

## ✨ คุณสมบัติเด่นของระบบ (Core Features)

### 1. ⚡ Real-time Tracking & 100% TOS Safe
* **คำนวณเงินสดทันใจ:** ติดตามการได้รับ N-Meseta และคำนวณอัตราความเร็ว Meseta ต่อชั่วโมง (M/hr) อัตโนมัติ
* **ปลอดภัยจากการแบน 100%:** อ่านข้อมูลผ่านไฟล์ข้อความ `ActionLog` ที่ตัวเกม PSO2:NGS สร้างขึ้นในเครื่องเท่านั้น ไม่มีการอ่าน Memory ไม่มีการดัดแปลงไฟล์เกม ไม่มีการฉีด DLL (Zero Injection)
* **Item Watchlist Filter:** กรองติดตามเฉพาะไอเทมหายาก แคปซูลพิเศษ หรืออาวุธที่ต้องการได้ตามใจชอบ
* **Gadget Mode (Overlay):** หน้าต่างมินิมอลโปร่งใส เปิดลอยทับหน้าจอเกมโดยไม่เกะกะ มีทั้งโหมด Full และ Mini Meseta

### 2. ⚔️ ARKS War Room & ระบบพิกัด Sector + 4 Slots
* **ตารางพิกัดระดับกาแล็กซี:** ครอบคลุม Sector X: `[-12 .. +25]` และ Sector Y: `[-11 .. +9]` รวมทั้งสิ้น 798 Sectors
* **4 Quadrant Sub-cell Slots:** แบ่งแต่ละ Sector ออกเป็น 4 ช่องย่อย:
  - ช่อง `#1` (NW บนซ้าย) — เป้าหมาย 25,000,000 N-Meseta
  - ช่อง `#2` (NE บนขวา) — เป้าหมาย 25,000,000 N-Meseta
  - ช่อง `#3` (SW ล่างซ้าย) — เป้าหมาย 25,000,000 N-Meseta
  - ช่อง `#4` (SE ล่างขวา) — เป้าหมาย 25,000,000 N-Meseta
  - รวมเป้าหมายทั้ง Sector เท่ากับ **100,000,000 N-Meseta**
* **Smart Coordinate Parser:** วางพิกัดได้ทันที รองรับ 7 รูปแบบอินพุต (ทั้งแบบ 3 จำนวน, วงเล็บ, JSON, และข้อความคัดลอกจากเว็บ)
* **Zero-Login Architecture:** ตรวจจับชื่อตัวละครจริงในเกมจากไฟล์ Log อัตโนมัติและใช้เป็น Primary Key ทันที ไม่ต้องสร้างบัญชี ไม่ต้องจำรหัสผ่าน
* **Firebase Realtime Sync:** เธรดเบื้องหลังส่ง Telemetry สดขึ้น Google Firebase Realtime Database ด้วย Debounce 0.35 วินาที พร้อม Heartbeat ทุก 5 วินาที

### 3. 🛡️ C# .NET 6 WPF Native Tracker (V7.0.0-alpha)
* **ประสิทธิภาพระดับ Native:** เรนเดอร์ด้วยฮาร์ดแวร์กราฟิก ประหยัดทรัพยากรเครื่อง
* **AntiTamperGuard:** ระบบตรวจจับความถูกต้องของ Process ป้องกันการโกงตัวเลขสถิติ
* **Multi-Language Support:** รองรับภาษาไทย (TH), ภาษาอังกฤษ (EN), และภาษาญี่ปุ่น (JA)

---

## 🚀 วิธีการใช้งาน (Getting Started)

### การใช้งานทั่วไปสำหรับผู้เล่น
1. ดับเบิลคลิกเปิดโปรแกรมผ่าน `run_app.bat` หรือเปิดไฟล์ `.exe`
2. คลิกปุ่ม **"📂 จิ้มเลือกโฟลเดอร์ Log"** และเลือกโฟลเดอร์ Log ของเกม PSO2:NGS
   * *พาธเริ่มต้น: `Documents\SEGA\PHANTASYSTARONLINE2\log_ngs`*
3. เริ่มต้นฟาร์มในเกม ตัวเลขเงินและรายการไอเทมจะอัปเดตแบบเรียลไทม์ทันที!
4. หากต้องการร่วมสงคราม ให้คลิก **"⚔️ เข้าสู่สงคราม (ARKS War)"** ป้อนพิกัด Sector หรือเลือกช่อง Quadrant ที่ต้องการช่วยทีมยึดครอง

---

## 🧪 การรันชุดทดสอบ (Automated Testing)

โครงการนี้มีชุดทดสอบครอบคลุมทั้ง 2 แพลตฟอร์ม รวม **40 การทดสอบ** ซึ่งผ่านการรับรอง 100%:

```bash
# 1. ทดสอบระบบ Python (13 รายการ)
python -m pytest -v
# หรือดับเบิลคลิก run_test.bat

# 2. ทดสอบระบบ C# .NET 6 WPF (27 รายการ)
dotnet test NekoTracker.Tests/NekoTracker.Tests.csproj
```

---

## 📚 เอกสารประกอบโครงการ (Project Documentation)

* 📖 **[สารบัญและหลักธรรมาภิบาลเอกสาร (Doc/README.md)](Doc/README.md)**
* 🟢 **[สเปคระบบปัจจุบัน (ACTIVE_SPECIFICATION.md)](Doc/current/ACTIVE_SPECIFICATION.md)**
* 🟢 **[บันทึกประวัติวิศวกรรม (ENGINEERING_LOG.md)](Doc/current/ENGINEERING_LOG.md)**
* 🟢 **[คู่มือส่งต่องานสำหรับ AI Agents (AI_HANDOFF.md)](Doc/current/AI_HANDOFF.md)**
* 🔵 **[สถาปัตยกรรมระบบและการไหลของข้อมูล (ARCHITECTURE.md)](Doc/reference/ARCHITECTURE.md)**
* 🔵 **[ข้อกำหนดระบบพิกัด Sector และ 4 Slots (COORDINATE_SYSTEM.md)](Doc/reference/COORDINATE_SYSTEM.md)**
* 🔵 **[โครงสร้างข้อมูล Firebase RTDB (FIREBASE_WIRE_SCHEMA.md)](Doc/reference/FIREBASE_WIRE_SCHEMA.md)**
* 🔵 **[มาตรฐานความปลอดภัยและ AntiTamperGuard (SECURITY_ANTITAMPER.md)](Doc/reference/SECURITY_ANTITAMPER.md)**
* 🔴 **[คลังเอกสารและซอร์สโค้ดที่ปลดระวาง (Doc/archive/README.md)](Doc/archive/README.md)**

---

## 📜 Credits & License
* **Project Owner:** NEKO FAMILY TEAM SHIP 4 JP
* **Developer:** Vale3neko

### ⚠️ Terms of Use (เงื่อนไขการใช้งาน)
**[EN]** This program is created for the public benefit of the PSO2:NGS community. It is open for anyone to fork, modify, and develop further freely. However, **STRICTLY NO COMMERCIAL USE IS ALLOWED.** Do not sell, monetize, or use this software for any personal financial gain.

**[TH]** โปรแกรมนี้จัดทำขึ้นเพื่อประโยชน์สาธารณะแก่คอมมูนิตี้ผู้เล่น PSO2:NGS ผู้ใช้สามารถนำซอร์สโค้ดไปศึกษาหรือพัฒนาต่อยอดได้อย่างอิสระโดยไม่มีค่าใช้จ่าย **แต่ไม่อนุญาตให้นำไปใช้ในเชิงพาณิชย์ แสวงหาผลกำไร หรือนำไปขายต่อโดยเด็ดขาด**
