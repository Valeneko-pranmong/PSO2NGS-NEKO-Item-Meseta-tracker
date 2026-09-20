# 📦 [ARCHIVED] NEKO Item & Meseta Tracker — V6.0 Standalone Offline Specification

> ⚠️ **ARCHIVED / DEPRECATED — DO NOT USE FOR ACTIVE DEVELOPMENT (ห้ามใช้ในงานพัฒนาปัจจุบัน)**  
> **สถานะ:** `[ARCHIVE]` 🔴 — สเปคของรุ่นออฟไลน์ดั้งเดิมก่อนเพิ่มระบบเครือข่ายและสงคราม ARKS War Room  
> **เอกสารปัจจุบัน:** [`Doc/current/ACTIVE_SPECIFICATION.md`](../current/ACTIVE_SPECIFICATION.md)  

---

## 1. ขอบเขตดั้งเดิมของ V6.0 (Historical Scope)

ในเวอร์ชัน V6.0.0 เริ่มต้น ตัวโปรแกรมมีขอบเขตการทำงานเฉพาะการใช้งานส่วนบุคคลแบบออฟไลน์ 100%:
* ติดตามเฉพาะเงิน N-Meseta ที่ได้รับระหว่างการฟาร์ม
* คำนวณอัตราความเร็ว Meseta ต่อชั่วโมง (M/hr) แบบพื้นฐาน
* มีหน้าจอแดชบอร์ดหลักและหน้าต่าง Overlay ขนาดเล็ก
* ไม่มีการเชื่อมต่อกับเซิร์ฟเวอร์ภายนอก ไม่มีการส่ง Telemetry ใดๆ
* บันทึกการตั้งค่า Watchlist ลงใน `%APPDATA%\NekoTrackerOffline\ngs_tracker_config.json`

---

## 2. สิ่งที่ได้รับการยกระดับในสถาปัตยกรรมปัจจุบัน

ตั้งแต่รุ่น V6.1.0 เป็นต้นมา ระบบได้รับการยกเครื่องสถาปัตยกรรมขนานใหญ่:
1. การเพิ่มสถาปัตยกรรม **EventBus** แบบ Decoupled Pub/Sub
2. การเพิ่มโหมดสงคราม **ARKS War Room** พร้อมระบบพิกัด Sector [-12..25, -11..9] และ 4 Sub-cell Slots (NW, NE, SW, SE)
3. การส่ง Telemetry แบบ Real-time ขึ้น **Google Firebase Realtime Database** ด้วย Debounce Worker Thread
4. การพัฒนารุ่นเนทีฟ **C# .NET 6 WPF (V7.0.0-alpha)** พร้อมระบบรักษาความปลอดภัย **AntiTamperGuard**
