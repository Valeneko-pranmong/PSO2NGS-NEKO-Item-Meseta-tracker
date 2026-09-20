# 📦 NEKO Tracker — Legacy WPF Native Tracker Archive (คลังโครงการ C# WPF ที่ปลดระวาง)

> **สถานะ:** `[ARCHIVED]` 🔴 — โครงการนี้ถูกยกเลิกและปลดระวางอย่างเป็นทางการ  
> **วันที่ปลดระวาง:** 2026-09  
> **ระบบหลักที่เข้ามารับหน้าที่แทน (Active Source of Truth):** Python Tracker (`meseta_tracker.py`, `dashboard_ui.py`, `overlay_ui.py`, `modules/war_mode/`)

---

## 1. ภาพรวมและเหตุผลการยกเลิก (Background & Cancellation Rationale)

ไดเรกทอรีนี้เก็บรักษาซอร์สโค้ดของเนทีฟแอปพลิเคชัน **C# .NET 6 WPF (`NekoTracker-WPF/`)** และชุดทดสอบ **`NekoTracker.Tests/`** ซึ่งเดิมได้รับการพัฒนาเป็นโครงการคู่ขนาน (Dual-stack Prototype) 

### สาเหตุการยกเลิกการพัฒนาเวอร์ชัน WPF:
1. **การรวมศูนย์การพัฒนา (Ecosystem Consolidation):** การพัฒนาสองโค้ดเบสคู่ขนาน (Python และ C# WPF) สร้างภาระในการบำรุงรักษา (Maintenance Overhead) โดยเฉพาะการซิงค์สถาปัตยกรรม ARKS War Room, Wire Schema, และระบบพิกัด Sector + 4 Slots
2. **ความยืดหยุ่นและคอมมูนิตี้ (Agility & Modularity):** เวอร์ชัน Python (CustomTkinter + EventBus) มีความยืดหยุ่นสูง สามารถปรับแต่ง UI โหมด ARKS War Room, ทำงานร่วมกับเครื่องมือวิเคราะห์ และปรับเปลี่ยน Logic การตรวจจับ Log ของ PSO2:NGS ได้รวดเร็วกว่า
3. **ความต้องการของผู้ใช้งาน:** มุ่งเน้นการพัฒนา Python Tracker ให้เป็นแอปพลิเคชันที่สมบูรณ์แบบ ทั้งประสิทธิภาพ ความเสถียร ระบบ Telemetry สด และตัวติดตั้ง Windows (Standalone Executable)

---

## 2. โครงสร้างไฟล์ที่ถูกเก็บรักษา (Archived Inventory)

| ไดเรกทอรี / ไฟล์ | หน้าที่เดิม | สภาพก่อนปลดระวาง |
| :--- | :--- | :--- |
| `archive/legacy_wpf/NekoTracker-WPF/` | ซอร์สโค้ดหลักของ C# .NET 6 WPF Tracker | มีหน้าต่าง MainWindow, OverlayWindow, ActionLogParser, LogWatcher, AntiTamperGuard |
| `archive/legacy_wpf/NekoTracker.Tests/` | ชุดทดสอบ Unit Tests ของ C# (xUnit) | มีการทดสอบ AntiTamper, Localization, LogParser, Versioning (39 การทดสอบ) |

---

## 3. กฎเกณฑ์การควบคุม (Governance Rules)

1. **ห้ามนำมาคอมไพล์ใน Production:** ไปป์ไลน์การบิลด์ (`installer/build_installer.py`, `build_installer.bat`) จะต้องไม่เรียกใช้ `dotnet publish` หรือ `dotnet test` อีกต่อไป
2. **ห้ามนำเข้าสู่ตัวติดตั้ง (Installer Package):** ตัวติดตั้ง Windows ทางการจะบรรจุเฉพาะ Python Tracker (`meseta_tracker.py`) เท่านั้น
3. **การรักษาประวัติ (Historical Provenance):** โค้ดทั้งหมดในโฟลเดอร์นี้ถูกย้ายด้วยคำสั่ง `git mv` เพื่อรักษาประวัติการคอมมิตไว้ตรวจสอบย้อนหลัง
