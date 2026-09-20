# 🔒 [ARCHIVED] NEKO Tracker — Legacy Supabase Authentication Specification

> ⚠️ **ARCHIVED / DEPRECATED — DO NOT USE FOR ACTIVE DEVELOPMENT (ห้ามใช้ในงานพัฒนาปัจจุบัน)**  
> **สถานะ:** `[ARCHIVE]` 🔴 — ปลดระวางอย่างเป็นทางการเมื่อกันยายน 2026  
> **เอกสารและระบบที่เข้ามารับหน้าที่แทน:** [`Doc/current/ACTIVE_SPECIFICATION.md`](../current/ACTIVE_SPECIFICATION.md) และ [`Doc/reference/SECURITY_ANTITAMPER.md`](../reference/SECURITY_ANTITAMPER.md)  
> **ซอร์สโค้ดเดิม:** ถูกย้ายไปเก็บรักษาที่ [`archive/legacy_auth/`](../../archive/legacy_auth/)  

---

## 1. ประวัติและเหตุผลในการปลดระวาง (Retirement Rationale)

ในรุ่นพัฒนาช่วงต้น ระบบเคยใช้ระบบยืนยันตัวตนผ่านบริการ Supabase (`AuthService` และ `AuthFrame`) โดยให้ผู้ใช้งานกรอกชื่อผู้ใช้และรหัสผ่านเพื่อเข้าใช้งานโหมด ARKS War Room

อย่างไรก็ดี สถาปัตยกรรมดังกล่าวมีข้อเสียสำคัญ:
1. ผู้เล่นเกม PSO2:NGS ต้องการความรวดเร็วในการเปิดใช้งานช่วง PSE Burst และไม่อยากต้องมานั่งจำรหัสผ่านหรือล็อกอินซ้ำ
2. การให้ผู้เล่นกรอกรหัสผ่านสร้างความลังเลและลดความเชื่อมั่นด้านความปลอดภัย
3. ตัวเกม PSO2:NGS มีการบันทึกชื่อตัวละครและรหัสผู้เล่นลงในไฟล์ `ActionLog` อยู่แล้วอย่างเป็นทางการ

ด้วยเหตุนี้ ระบบจึงถูกปฏิรูปอย่างสิ้นเชิงไปสู่ **Zero-Login Operative Auto-Detection** โดยดึงชื่อตัวละครในเกมมาเป็น Primary Key โดยตรง ทำให้ระบบ Login เดิมถูกถอดออกจากตัวโปรแกรมหลัก 100% (ผ่านการรับรองด้วย Unit Test `test_login_system_removed_from_app`)

---

## 2. โครงสร้างเดิมที่ปลดระวาง (Historical Structure - For Audit Only)

เดิมระบบประกอบด้วย 2 คลาสหลัก:
* `modules/auth/auth_service.py` (`AuthService`):
  - เชื่อมต่อ Supabase Client ไปยัง URL โครงการเดิม
  - จัดการเซสชันล็อกอินลง `%APPDATA%\NekoTrackerOffline\auth_session.json`
* `modules/auth/auth_view.py` (`AuthFrame`):
  - หน้าจอ CustomTkinter สำหรับกรอก Username และ Password
  - โหมดสลับระหว่าง Sign In และ Operative Callsign Register

---

## 3. ข้อควรระวัง

ห้ามฟื้นฟูหรือนำเข้าโมดูล `AuthService` กลับสู่ `meseta_tracker.py` หรือ `war_view.py` เป็นอันขาด
