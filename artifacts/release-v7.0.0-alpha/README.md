# 🌸 NEKO Item & Meseta Tracker — Release V7.0.0-alpha Distribution Artifacts

> **สถานะ:** `[ARCHIVE]` 🔴 — อาร์ติแฟกต์ต้นแบบที่ปลดระวางแล้ว (Archived Prototype Distribution)  
> **รุ่น:** C# WPF Native Version `7.0.0-alpha` (ยกเลิกการพัฒนาแล้ว)  
> **ทีมพัฒนา:** NEKO FAMILY TEAM SHIP 4 JP / Vale3neko  
> **แพลตฟอร์ม:** Windows 10 / Windows 11 (64-bit)  
> **การเผยแพร่จริงปัจจุบัน (Active Distribution):** [`artifacts/release-v6.1.0/`](../release-v6.1.0/) (Python Tracker V6.1.0 / V7.1.0)

---

## 📦 ตารางจำแนกสถานะอาร์ติแฟกต์ (Artifact Lifecycle Classification)

| ไฟล์อาร์ติแฟกต์ (Artifact Name) | สถานะ (Tier) | บทบาทและรายละเอียด |
| :--- | :--- | :--- |
| **`NekoTracker-Setup-v7.0.0-alpha.exe`** | `[ARCHIVE]` 🔴 | **ปลดระวาง (Archived):** ตัวติดตั้งต้นแบบ C# WPF ที่ยกเลิกการพัฒนาแล้ว เก็บไว้เพื่ออ้างอิงย้อนหลัง |
| **`SHA256SUMS.txt`** | `[REFERENCE]` 🔵 | **ตรวจสอบความถูกต้อง (Verification):** ค่าแฮช SHA-256 ของตัวติดตั้งเดิม |
| **`../release-v6.1.0/`** | `[CURRENT]` 🟢 | **ใช้งานจริง (Active):** แพ็กเกจตัวติดตั้งทางการของ Python Tracker |
| **`build/wpf_publish/`** | `[REFERENCE]` 🔵 | **เก็บอ้างอิง (Reference):** ผลลัพธ์จากการคอมไพล์ .NET 6 Self-contained WPF |
| **`dist/NekoTracker/`** | `[REFERENCE]` 🔵 | **เก็บอ้างอิง (Reference):** โฟลเดอร์ผลลัพธ์จาก PyInstaller Onedir Distribution |
| **`archive/legacy_auth/`** | `[ARCHIVE]` 🔴 | **ห้ามใช้งาน (Deprecated):** ซอร์สโค้ดระบบล็อกอินเดิมที่ปลดระวางแล้ว |

---

## 🛡️ ลายเซ็นดิจิทัลและแฮชความปลอดภัย (Cryptographic Checksums)

ตรวจสอบความถูกต้องของไฟล์ก่อนการใช้งานด้วยค่า SHA-256:

```text
b22ede9fb76a946639cd70964ed0c3f9afae780bfd4a7b7ae75c36e3a944bd6f  NekoTracker-Setup-v7.0.0-alpha.exe
```

* **ขนาดไฟล์:** ~105.12 MB (110,230,128 bytes)
* **กลไกการบีบอัด:** LZMA2/Ultra64 Solid Compression (Inno Setup 6)
* **ความปลอดภัย:** 100% TOS Safe (Passive ActionLog Ingestion Only, Zero-Login)

---

## 🚀 สรุปสิ่งที่มีในชุดติดตั้ง (Included Components)

1. **NEKO Item & Meseta Tracker (Primary — V7.0.0-alpha WPF Native):**
   - ตัวโปรแกรมหลักเนทีฟ Windows พัฒนาด้วย C# .NET 6 WPF พร้อม Pastel Theme สวยงาม
   - ประสิทธิภาพสูง เรนเดอร์ด้วยฮาร์ดแวร์กราฟิก ประหยัดทรัพยากร CPU/RAM
   - ระบบความปลอดภัย **AntiTamperGuard** ป้องกันการดัดแปลงและโกงข้อมูลในตัวโปรแกรม
   - ระบบอ่าน `ActionLog` ประสิทธิภาพสูง แปลงข้อความเป็น Strong-typed Record
   - รองรับหลายภาษา: ไทย (TH), อังกฤษ (EN), และญี่ปุ่น (JA) พร้อมสลับภาษาแบบไดนามิก
   - หน้าต่าง Overlay ลอยทับเกมแบบเนทีฟ
2. **Companion Engine (Python V6.1.0 with ARKS War Room):**
   - ติดตั้งไว้ในโฟลเดอร์ `python-v6/` ภายในไดเรกทอรีโปรแกรม
   - รองรับโหมด **ARKS War Room** แผนที่ 798 Sectors และระบบซิงค์สดขึ้น Firebase Realtime Database
3. **การลงทะเบียนระบบ Windows:**
   - ทางลัดเปิดโปรแกรมใน Start Menu:
     - `NEKO Item & Meseta Tracker (V7.0.0 Alpha)` (โปรแกรมหลัก)
     - `NEKO Tracker (Python V6.1.0 Edition)` (โปรแกรมเสริม)
   - ไอคอนทางลัดบน Desktop
   - ตัวถอนการติดตั้งอย่างสมบูรณ์ (`unins000.exe` จัดการผ่าน Windows Settings ได้อย่างหมดจด)

---

## 📖 วิธีการติดตั้ง (Installation Guide)

### ภาษาไทย (TH)
1. ดาวน์โหลดไฟล์ `NekoTracker-Setup-v7.0.0-alpha.exe`
2. ดับเบิลคลิกเพื่อเปิดตัวติดตั้ง (รองรับการติดตั้งทั้งแบบผู้ใช้ทั่วไปและสิทธิ์ Administrator)
3. เลือกตำแหน่งโฟลเดอร์ปลายทาง (ค่าเริ่มต้น: `%ProgramFiles%\NEKO Item & Meseta Tracker`)
4. เลือกว่าต้องการสร้างไอคอนบน Desktop หรือไม่ แล้วกด **Install**
5. เมื่อติดตั้งเสร็จสิ้น ติ๊กถูกเปิดโปรแกรมเพื่อเริ่มใช้งานได้ทันที

### English (EN)
1. Download `NekoTracker-Setup-v7.0.0-alpha.exe`.
2. Double-click the installer executable to launch the setup wizard.
3. Choose the destination directory (Default: `%ProgramFiles%\NEKO Item & Meseta Tracker`).
4. Select optional desktop shortcut and click **Install**.
5. Launch the tracker immediately upon completion.
