# 📦 NEKO Tracker — Code Archive Inventory (คลังโค้ดและส่วนประกอบที่ปลดระวาง)

> **ARCHIVED / DEPRECATED — DO NOT USE FOR ACTIVE DEVELOPMENT (ห้ามใช้ในงานพัฒนาปัจจุบัน)**
>
> ไดเรกทอรีนี้เก็บรักษาซอร์สโค้ดและโมดูลรุ่นเก่าที่ถูกปลดระวางจากการใช้งานจริง (Production) เพื่อวัตถุประสงค์ในการตรวจสอบย้อนหลัง (Historical Provenance / Audit Trail) เท่านั้น **ห้ามนำโมดูลในโฟลเดอร์นี้ไป import หรือเชื่อมต่อกับโมดูลหลักของระบบเด็ดขาด**

---

## 📋 รายการโมดูลที่ปลดระวาง (Archived Modules Inventory)

| โมดูล / ไดเรกทอรี | หมวดหมู่ | วันที่ปลดระวาง | สาเหตุการปลดระวาง | ระบบที่เข้ามารับหน้าที่แทน (Source of Truth) |
| :--- | :--- | :--- | :--- | :--- |
| `archive/legacy_auth/` | Authentication | 2026-09 | เปลี่ยนจากระบบ Login ด้วยบัญชี Supabase / Password ไปเป็นสถาปัตยกรรม **Zero-Login Operative Auto-Detection** ที่อ่านชื่อตัวละครในเกมผ่านไฟล์ ActionLog โดยตรงแบบอัตโนมัติ ทำให้ผู้ใช้ไม่ต้องกรอก User/Pass และไม่มีความเสี่ยงด้านความปลอดภัย | `modules/war_mode/war_service.py`<br>`modules/event_bus.py` |
| `archive/legacy_wpf/` | Windows Native Desktop (WPF) | 2026-09 | ยกเลิกการพัฒนาเวอร์ชัน C# WPF กลับไปยึด Python Tracker (CustomTkinter + EventBus + ARKS War Room) เป็นแกนหลักของการพัฒนาเพียงหนึ่งเดียว เพื่อความคล่องตัวในการพัฒนา ความสอดคล้องของระบบ Telemetry และลดความซ้ำซ้อนของโค้ดเบส | `meseta_tracker.py`<br>`dashboard_ui.py`<br>`overlay_ui.py`<br>`modules/war_mode/` |

---

## 🚫 กฎเกณฑ์การควบคุม (Governance Rules)

1. **ห้าม Import ใน Production:** โมดูลที่อยู่ใน `archive/` จะต้องไม่ถูกเรียกใช้โดย `meseta_tracker.py`, `dashboard_ui.py`, `overlay_ui.py`, หรือโมดูลอื่นใน `modules/`
2. **ห้ามลบประวัติ Git:** ไฟล์ในโฟลเดอร์นี้ถูกย้ายด้วยคำสั่ง `git mv` เพื่อรักษา Git Blame และประวัติการคอมมิตไว้ครบถ้วน
3. **ตรวจสอบความถูกต้องด้วย Automated Tests:** ชุดทดสอบ `tests/test_tracker_modules.py` (เช่น `test_login_system_removed_from_app`) จะทำหน้าที่รับประกันว่าระบบ Login ถูกถอดออกจาก Workflow หลักอย่างสมบูรณ์
