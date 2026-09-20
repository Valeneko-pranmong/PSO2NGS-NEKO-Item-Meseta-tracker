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
  - ตรวจสอบความถูกต้องของชุดทดสอบทั้ง Python (13/13 ผ่าน) และ C# (27/27 ผ่าน) โดยไม่มีข้อผิดพลาดถดถอย
