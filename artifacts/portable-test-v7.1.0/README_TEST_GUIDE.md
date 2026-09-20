# 🌸 NEKO Item & Meseta Tracker — Portable Test Package (V7.1.0)

> **สถานะ:** `[PORTABLE TEST ARTIFACT]` 🟢  
> **รุ่น:** `7.1.0` (Pure Python Modular Architecture)  
> **วัตถุประสงค์:** ชุดทดสอบการทำงานแบบ Standalone ก่อนสร้างและติดตั้งผ่าน Installer  

---

## 🚀 ไฟล์เรียกใช้งานหลัก (Launchers)

| ไฟล์ Script | หน้าที่ |
| :--- | :--- |
| **`1_Run_NekoTracker_Test.bat`** | เปิดตัวโปรแกรมหลัก Python Tracker V7.1.0 (พร้อม War Room & Firebase Sync) |
| **`2_Start_Mock_Log_Feed.bat`** | เริ่มสตรีม ActionLog จำลองสด (Drop เงิน, ไอเทม, PSE Burst) ลงโฟลเดอร์ `sample_logs/` |
| **`3_Quick_Test_All_In_One.bat`** | รันตัวจำลอง Log พร้อมเปิด NekoTracker ให้อัตโนมัติในคลิกเดียว |

---

## 🧪 ขั้นตอนการทดสอบ (Testing Workflow)

1. ดับเบิ้ลคลิก `3_Quick_Test_All_In_One.bat`
2. บนหน้าต่าง Tracker คลิกปุ่ม **"เลือกโฟลเดอร์ Log"** แล้วเลือกพาธ `sample_logs`
3. ตรวจสอบการทำงาน:
   - **Zero-Login Detection:** พบชื่อตัวละคร `Vale3neko` จากไฟล์ Log ทันที
   - **Meseta Counter & M/hr:** ยอดเงินวิ่งนับสดตามจังหวะ PSE Burst
   - **Item Drop Watchlist:** แคปซูลและวัตถุดิบปรากฏในรายการ
   - **Overlay Window:** หน้าต่าง Overlay ลอยทับหน้าจอแสดงผลถูกต้อง
   - **ARKS War Room:** สลับหน้าจอ War Room, ระบุพิกัด `15, -6, 2` ส่ง Telemetry ด้วย Version `7.1.0`
