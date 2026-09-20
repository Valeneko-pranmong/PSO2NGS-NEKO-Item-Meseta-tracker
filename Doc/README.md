# 📚 NEKO Item & Meseta Tracker — Master Documentation Governance (สารบัญเอกสารหลัก)

> **ศูนย์รวมการกำกับดูแลเอกสาร สถาปัตยกรรมระบบ และคู่มือการพัฒนาระบบ NEKO Tracker (PSO2:NGS)**
> จัดหมวดหมู่เอกสารและส่วนประกอบตามมาตรฐาน **Repository Artifact Governance** แบ่งออกเป็น 3 ระดับชั้น (Canonical Lifecycle Tiers) เพื่อป้องกันความสับสนระหว่างเอกสารที่ใช้งานจริง เอกสารอ้างอิง และข้อกำหนดที่ปลดระวางแล้ว

---

## 🏛️ สรุปผังโครงสร้างเอกสาร (Documentation Governance Matrix)

| หมวดหมู่ (Classification) | สถานะ (Badge) | ระดับการใช้งาน | ขอบเขตหน้าที่และความรับผิดชอบ | พาธไดเรกทอรี |
| :--- | :--- | :--- | :--- | :--- |
| **Current** | `[CURRENT]` 🟢 | **ใช้งานจริง (Active)** | สเปคการทำงานปัจจุบัน, บันทึกการวิศวกรรม, และ AI Operational Handoff สำหรับการพัฒนาต่อยอด | [`Doc/current/`](current/) |
| **Reference** | `[REFERENCE]` 🔵 | **เก็บอ้างอิง (Reference)** | ผังสถาปัตยกรรมระบบ, โครงสร้างระบบพิกัด Sector + 4 Slots, Wire Contract Firebase, และระบบ Anti-Tamper | [`Doc/reference/`](reference/) |
| **Archive** | `[ARCHIVE]` 🔴 | **ห้ามใช้ในงานปัจจุบัน (Deprecated)** | ข้อกำหนดและซอร์สโค้ดของระบบที่ถูกปลดระวางแล้ว (เช่น ระบบ Login เดิม) เก็บไว้เพื่อการสืบค้นย้อนหลังเท่านั้น | [`Doc/archive/`](archive/) |

---

## 📑 สารบัญเอกสารทั้งหมด (Documentation Directory Index)

### 1. 🟢 ระดับงานปัจจุบัน (Current — ใช้งานจริง)
* [`Doc/current/ACTIVE_SPECIFICATION.md`](current/ACTIVE_SPECIFICATION.md) — ข้อกำหนดทางเทคนิคฉบับสมบูรณ์ของ V6.1.0 (Python Modular Tracker + ARKS War Room) และ V7.0.0-alpha (C# .NET 6 WPF Native Tracker)
* [`Doc/current/ENGINEERING_LOG.md`](current/ENGINEERING_LOG.md) — บันทึกประวัติวิศวกรรมและวิวัฒนาการสถาปัตยกรรมระบบ ตั้งแต่ V1 จนถึงรุ่นล่าสุด
* [`Doc/current/AI_HANDOFF.md`](current/AI_HANDOFF.md) — คู่มือการส่งต่องานสำหรับ AI Agents และวิศวกรซอฟต์แวร์ (สภาพแวดล้อม, คำสั่งรัน, การทดสอบ, จุดเชื่อมต่อโค้ด)

### 2. 🔵 ระดับเก็บอ้างอิง (Reference — เอกสารอ้างอิงทางเทคนิค)
* [`Doc/reference/ARCHITECTURE.md`](reference/ARCHITECTURE.md) — ผังสถาปัตยกรรมระบบ, ท่อประมวลผลข้อมูล (Data Pipeline), EventBus และการทำงานแบบ Multi-threading
* [`Doc/reference/COORDINATE_SYSTEM.md`](reference/COORDINATE_SYSTEM.md) — ข้อกำหนดระบบพิกัด Sector [-12..25, -11..9] พร้อม 4 ช่องย่อย (Quadrant Slots), พิกัด Landmark สำคัญ, และไวยากรณ์การแปลงค่าพิกัด
* [`Doc/reference/FIREBASE_WIRE_SCHEMA.md`](reference/FIREBASE_WIRE_SCHEMA.md) — โครงสร้างข้อมูล JSON Wire Contract ของ Google Firebase Realtime Database (`/operatives`, `/sectors`, `/activity_feed`)
* [`Doc/reference/SECURITY_ANTITAMPER.md`](reference/SECURITY_ANTITAMPER.md) — การรับรองความปลอดภัยตามกฎเกม (100% TOS Safe, Passive Log Parsing) และการทำงานของระบบ AntiTamperGuard

### 3. 🔴 ระดับปลดระวาง (Archive — ประวัติและข้อกำหนดเก่า)
* [`Doc/archive/README.md`](archive/README.md) — สารบัญและนโยบายกำกับดูแลส่วนประกอบที่ปลดระวาง
* [`Doc/archive/LEGACY_LOGIN_SPEC.md`](archive/LEGACY_LOGIN_SPEC.md) — ข้อกำหนดระบบ Login เดิมผ่าน Supabase (ปลดระวางเนื่องจากเปลี่ยนเป็น Zero-Login Auto-Detection)
* [`Doc/archive/V6_OFFLINE_TRACKER_SPEC.md`](archive/V6_OFFLINE_TRACKER_SPEC.md) — ข้อกำหนดระบบ Tracker รุ่นแรกก่อนการเพิ่มโหมด ARKS War Room

---

## ⚖️ กฎเกณฑ์สำหรับนักพัฒนาและ AI Agents (Developer Rules of Engagement)

1. **ยึดถือ Current เป็น Source of Truth:** เมื่อมีการแก้ไข ปรับปรุง หรือเพิ่มเติมฟังก์ชันการทำงาน ให้ศึกษาจาก [`Doc/current/ACTIVE_SPECIFICATION.md`](current/ACTIVE_SPECIFICATION.md) เป็นหลัก
2. **ห้ามเชื่อมต่อกับส่วนที่ปลดระวาง:** โค้ดในโฟลเดอร์ [`archive/`](../archive/) และเอกสารใน [`Doc/archive/`](archive/) ถูกปลดระวางแล้ว ห้ามนำกลับมา import หรือผูกกับ production pipeline
3. **รักษาความปลอดภัยและเงื่อนไข TOS:** โปรแกรมจะต้องอ่านข้อมูลจากไฟล์ข้อความ `ActionLog` ในเครื่องของผู้เล่นเท่านั้น ห้ามอ่าน memory, ห้ามแทรกแซงตัวเกม (no injection), และไม่มีการดัดแปลงไฟล์เกม
4. **ตรวจสอบก่อน Commit:** ทุกการเปลี่ยนแปลงโค้ดจะต้องผ่านการทดสอบ regression เสมอ:
   - Python Test Suite: `python -m pytest -v` (ต้องผ่าน 100%)
   - C# WPF Test Suite: `dotnet test NekoTracker.Tests/NekoTracker.Tests.csproj` (ต้องผ่าน 100%)
