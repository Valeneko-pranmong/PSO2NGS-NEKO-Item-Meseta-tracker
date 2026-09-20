# 🌸 NEKO Item & Meseta Tracker — Release v6.1.0 Distribution Artifacts

> **สถานะ:** `[CURRENT]` 🟢 — ไฟล์ติดตั้งและชุดแพ็กเกจทางการสำหรับผู้ใช้งานจริง (Active Production Distribution)  
> **รุ่น:** Python Version `6.1.0` / C# WPF Version `7.0.0-alpha` (Dual Architecture)  
> **ผู้พัฒนา:** NEKO FAMILY TEAM SHIP 4 JP / Vale3neko  
> **แพลตฟอร์ม:** Windows 10 / Windows 11 (64-bit)

---

## 📦 ตารางจำแนกสถานะอาร์ติแฟกต์ (Artifact Lifecycle Classification)

| ไฟล์อาร์ติแฟกต์ (Artifact Name) | สถานะ (Tier) | บทบาทและรายละเอียด |
| :--- | :--- | :--- |
| **`NekoTracker-Setup-v6.1.0.exe`** | `[CURRENT]` 🟢 | **ใช้งานจริง (Active):** ตัวติดตั้งแบบ One-Click Installer สำหรับผู้ใช้งานทั่วไป ครอบคลุมทั้งตัวโปรแกรมหลัก Python V6.1.0 และ WPF Native V7.0.0-alpha |
| **`SHA256SUMS.txt`** | `[CURRENT]` 🟢 | **ตรวจสอบความถูกต้อง (Verification):** ค่าแฮชทางคณิตศาสตร์ SHA-256 เพื่อความโปร่งใสและตรวจสอบความสมบูรณ์ของไฟล์ |
| **`build/wpf_publish/`** | `[REFERENCE]` 🔵 | **เก็บอ้างอิง (Reference):** ผลลัพธ์จากการคอมไพล์ .NET 6 Self-contained WPF |
| **`dist/NekoTracker/`** | `[REFERENCE]` 🔵 | **เก็บอ้างอิง (Reference):** โฟลเดอร์ผลลัพธ์จาก PyInstaller Onedir Distribution |
| **`archive/legacy_auth/`** | `[ARCHIVE]` 🔴 | **ห้ามใช้งาน (Deprecated):** ซอร์สโค้ดระบบล็อกอินเดิมที่ปลดระวางแล้ว |

---

## 🛡️ ลายเซ็นดิจิทัลและแฮชความปลอดภัย (Cryptographic Checksums)

ตรวจสอบความถูกต้องของไฟล์ก่อนการใช้งานด้วยค่า SHA-256:

```text
0aed216a755cf7552bb131f4fd7d9cbae12e62b4308f76519d80d82367f5b26d  NekoTracker-Setup-v6.1.0.exe
```

* **ขนาดไฟล์:** ~105.42 MB
* **กลไกการบีบอัด:** LZMA2/Ultra64 Solid Compression (Inno Setup 6)
* **การติดตั้ง:** Per-User Local AppData (`%LOCALAPPDATA%\NEKO FAMILY\NekoTracker`, `PrivilegesRequired=lowest`)
* **ระบบความปลอดภัย:** 100% TOS Safe (Passive File Ingestion Only)

---

## 🚀 สรุปสิ่งที่มีในชุดติดตั้ง (Included Components)

1. **NEKO Item & Meseta Tracker (Main Application — V6.1.0):**
   - ตัวโปรแกรมหลักภาษา Python พร้อม UI พาสเทลด้วย CustomTkinter
   - ติดตามรายได้ Meseta และคำนวณ Meseta ต่อชั่วโมง (M/hr) แบบเรียลไทม์
   - หน้าต่าง Gadget Overlay (Full Mode & Mini Meseta Mode)
   - โหมด **ARKS War Room** รองรับพิกัด Sector + 4 Quadrant Sub-cell Slots ทั่ว 798 Sectors
   - ระบบซิงค์ข้อมูลสดขึ้น Google Firebase Realtime Database
   - สถาปัตยกรรม **Zero-Login** ดึงชื่อตัวละครจาก `ActionLog` อัตโนมัติ ปลอดภัย ไม่ต้องใช้รหัสผ่าน
2. **NEKO Tracker WPF (Native Hardware-Accelerated Preview — V7.0.0-alpha):**
   - ตัวโปรแกรมเวอร์ชันเนทีฟ C# .NET 6 WPF
   - เรนเดอร์ด้วยฮาร์ดแวร์กราฟิก ประหยัดทรัพยากรเครื่อง
   - ระบบความปลอดภัย **AntiTamperGuard** ป้องกันการโกงและการปลอมแปลง Process
   - รองรับภาษาอังกฤษ (EN), ญี่ปุ่น (JA), และไทย (TH)
3. **การลงทะเบียนระบบ Windows:**
   - ไอคอนทางลัดบน Desktop (ทางเลือก)
   - เมนูใน Windows Start Menu
   - ระบบถอนการติดตั้งอย่างสมบูรณ์ (Clean Uninstaller) ผ่าน Windows Settings > Installed Apps

---

## 📖 วิธีการติดตั้ง (Installation Guide)

### ภาษาไทย (TH)
1. ดาวน์โหลดไฟล์ `NekoTracker-Setup-v6.1.0.exe`
2. ดับเบิลคลิกเพื่อเปิดตัวติดตั้ง
3. เลือกตำแหน่งที่ต้องการติดตั้ง (ค่าเริ่มต้น: `%ProgramFiles%\NEKO Item & Meseta Tracker` หรือตามที่ผู้ใช้กำหนด)
4. เลือกว่าต้องการสร้างไอคอนบน Desktop หรือไม่
5. คลิก **Install** จนเสร็จสิ้นและเปิดใช้งานโปรแกรมได้ทันที

### English (EN)
1. Download `NekoTracker-Setup-v6.1.0.exe`.
2. Double-click the installer executable to start the setup wizard.
3. Choose your desired destination folder (Default: `%ProgramFiles%\NEKO Item & Meseta Tracker`).
4. Optionally check "Create a desktop shortcut".
5. Click **Install** and launch the tracker immediately upon completion.
