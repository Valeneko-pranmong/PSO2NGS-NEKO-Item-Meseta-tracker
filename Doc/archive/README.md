# 🗄️ NEKO Item & Meseta Tracker — Documentation Archive (คลังเอกสารประวัติศาสตร์ที่ปลดระวาง)

> **ARCHIVED / DEPRECATED — DO NOT USE FOR ACTIVE DEVELOPMENT (ห้ามใช้ในงานพัฒนาปัจจุบัน)**
>
> เอกสารในโฟลเดอร์นี้เป็นข้อกำหนดและคู่มือของระบบรุ่นเก่าที่ถูกยกเลิกหรือแทนที่ด้วยสถาปัตยกรรมใหม่แล้ว เก็บรักษาไว้เพื่อการสืบค้นประวัติย้อนหลัง (Historical Provenance / Audit Trail) เท่านั้น  
> **แหล่งข้อมูลจริงสำหรับงานปัจจุบัน (Source of Truth):** โปรดดูที่ [`Doc/current/ACTIVE_SPECIFICATION.md`](../current/ACTIVE_SPECIFICATION.md)

---

## 📋 รายการเอกสารที่ปลดระวาง (Archived Documents Inventory)

| เอกสาร | สถานะเดิม | วันที่ปลดระวาง | สาเหตุที่ปลดระวาง | ระบบหรือเอกสารที่เข้ามาแทนที่ |
| :--- | :--- | :--- | :--- | :--- |
| [`LEGACY_LOGIN_SPEC.md`](LEGACY_LOGIN_SPEC.md) | ข้อกำหนดระบบ Authentication เดิม | 2026-09 | ยกเลิกระบบล็อกอินด้วย Supabase / บัญชีรหัสผ่าน เปลี่ยนเป็นระบบ **Zero-Login Operative Auto-Detection** ที่อ่านชื่อตัวละครจาก Log โดยตรง | [`Doc/reference/SECURITY_ANTITAMPER.md`](../reference/SECURITY_ANTITAMPER.md)<br>[`Doc/current/ACTIVE_SPECIFICATION.md`](../current/ACTIVE_SPECIFICATION.md) |
| [`V6_OFFLINE_TRACKER_SPEC.md`](V6_OFFLINE_TRACKER_SPEC.md) | ข้อกำหนดสถาปัตยกรรม Offline Tracker ดั้งเดิม | 2026-09 | ระบบเดิมรองรับเฉพาะการนับเงินออฟไลน์ ได้รับการอัปเกรดเป็นระบบ **ARKS War Room + Sector/4 Slots + Firebase Realtime Telemetry** | [`Doc/current/ACTIVE_SPECIFICATION.md`](../current/ACTIVE_SPECIFICATION.md) |
| [`WPF_NATIVE_SPEC.md`](WPF_NATIVE_SPEC.md) | ข้อกำหนดโปรเจกต์เนทีฟ C# .NET 6 WPF | 2026-09 | ยกเลิกโครงการเวอร์ชัน C# WPF เพื่อรวมศูนย์การพัฒนาทั้งหมดกลับสู่ **Python Tracker** เพียงระบบเดียว | [`Doc/current/ACTIVE_SPECIFICATION.md`](../current/ACTIVE_SPECIFICATION.md)<br>[`archive/legacy_wpf/`](../../archive/legacy_wpf/) |

---

## 🚫 ข้อห้ามสำหรับนักพัฒนา (Developer Invariants)

1. ห้ามนำโค้ดหรือข้อกำหนดในโฟลเดอร์นี้ไปอ้างอิงเป็นข้อกำหนดการทำงานปัจจุบัน
2. ห้ามสร้างฟอร์มกรอกรหัสผ่านหรือถามข้อมูลส่วนบุคคลของผู้เล่นตามเอกสารระบบล็อกอินเดิม
