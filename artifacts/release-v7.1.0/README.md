# 🌸 NEKO Item & Meseta Tracker — Release v7.1.0 Distribution Artifacts

> **สถานะ:** `[CURRENT]` 🟢 — ไฟล์ติดตั้งและชุดแพ็กเกจทางการสำหรับผู้ใช้งานจริงและเครื่องทดสอบ (Active Production & Testing Distribution)  
> **รุ่น:** Python Version `7.1.0` (Pure Python Modular Engine with ARKS War Room & Multi-Language Support)  
> **ผู้พัฒนา:** NEKO FAMILY TEAM SHIP 4 JP / Vale3neko  
> **แพลตฟอร์ม:** Windows 10 / Windows 11 (64-bit)

---

## 📦 ตารางจำแนกสถานะอาร์ติแฟกต์ (Artifact Lifecycle Classification)

| ไฟล์อาร์ติแฟกต์ (Artifact Name) | สถานะ (Tier) | บทบาทและรายละเอียด |
| :--- | :--- | :--- |
| **`NekoTracker-Setup-v7.1.0.exe`** | `[CURRENT]` 🟢 | **ใช้งานจริงและทดสอบ (Active):** ตัวติดตั้งแบบ Single-EXE Installer สำหรับผู้ใช้งานทั่วไปและเครื่องทดสอบ (ครอบคลุมตัวแอปหลัก Python V7.1.0, คู่มือ 3 ภาษา, ระบบ Uninstaller 4 ช่องทาง) |
| **`SHA256SUMS.txt`** | `[CURRENT]` 🟢 | **ตรวจสอบความถูกต้อง (Verification):** ค่าแฮชทางคณิตศาสตร์ SHA-256 เพื่อความโปร่งใสและตรวจสอบความสมบูรณ์ของไฟล์ |
| **`E2E_TEST_CHECKLIST.md`** | `[CURRENT]` 🟢 | **คู่มือเช็กลิสต์ QA (Testing):** แบบฟอร์มเช็กลิสต์การทดสอบ E2E สำหรับมนุษย์/คนเทส เริ่มตั้งแต่ตัวติดตั้งจนถึงถอนการติดตั้ง |
| **`../portable-test-v7.1.0/`** | `[REFERENCE]` 🔵 | **เก็บอ้างอิง (Reference):** โครงสร้างแพ็กเกจแบบ Portable สำหรับทดสอบก่อนคอมไพล์ตัวติดตั้ง |
| **`../release-v6.1.0/`** | `[ARCHIVE]` 🔴 | **เวอร์ชันเก่า (Archived Release):** ชุดติดตั้งรุ่นก่อนหน้าที่ปลดระวางแล้ว |
| **`../release-v7.0.0-alpha/`** | `[ARCHIVE]` 🔴 | **เวอร์ชันเก่า (Archived Release):** ชุดติดตั้งรุ่นทดลองเดิมที่ถูกระงับ (Revoked) |

---

## 🛡️ ลายเซ็นดิจิทัลและแฮชความปลอดภัย (Cryptographic Checksums)

ตรวจสอบความถูกต้องของไฟล์ก่อนการใช้งานด้วยค่า SHA-256:

```text
567c32d661e5a19396a67dbd7f992a1e3bce6cbf1a2c83c35aa16a3f4402ca4a  NekoTracker-Setup-v7.1.0.exe
```

* **ขนาดไฟล์:** ~22.18 MB
* **กลไกการบีบอัด:** LZMA2/Ultra64 Solid Compression (Inno Setup 6)
* **สถาปัตยกรรม:** 64-bit Windows (`ArchitecturesAllowed=x64compatible`)
* **การติดตั้ง:** Per-User Local AppData (`%LOCALAPPDATA%\NEKO FAMILY\NekoTracker`, `PrivilegesRequired=lowest`) ไม่ต้องใช้สิทธิ์ Administrator ไม่เด้งเตือน UAC
* **ระบบความปลอดภัย:** 100% TOS Safe (Passive File Ingestion Only) + Zero-Login Architecture

---

## 🚀 จุดเด่นในตัวติดตั้ง V7.1.0 สำหรับเครื่องเทสและผู้ใช้ทั่วไป

### 1. ระบบตัวโปรแกรมหลัก (Production Tracker — V7.1.0)
- **Zero-Login Architecture:** ดึงชื่อตัวละคร `CharacterName` และ `PlayerID` จาก `ActionLog` อัตโนมัติ ปลอดภัย 100% ไม่ถามรหัสผ่าน
- **Real-Time Meseta & Drops:** คำนวณรายได้สุทธิ, อัตราความเร็วเงินต่อชั่วโมง (M/hr) และรายการไอเท็มดรอป
- **Multi-Language Support (3 ภาษา):** สลับภาษาอังกฤษ (English), ไทย (ไทย), และญี่ปุ่น (日本語) ได้สดทันที
- **In-App User Guide:** หน้าต่างคู่มือการใช้งานและคำแนะนำระบบสงครามในตัว รองรับ 3 ภาษา พร้อมปุ่มคัดลอกลิงก์ Discord คอมมูนิตี้
- **ARKS War Room (Coordinate War Engine V9):** รองรับพิกัด 798 Sectors และ 4 Quadrant Slots พร้อมระบบ Standby Presence และซิงค์สด Realtime ขึ้น Cloud
- **AntiTamperGuard V7.1.0:** 10 เกราะป้องกันความสมบูรณ์ของข้อมูลและเพิกถอนเวอร์ชันที่มีช่องโหว่

### 2. ชุดเครื่องมือทดสอบสำหรับเครื่องเทสอื่นๆ (Testing Tools Included)
- **`NekoLogSimulator.exe` (Standalone Binary):** โปรแกรมจำลองการดรอปเงินและไอเทมแบบคอมไพล์สำเร็จรูป เครื่องเทสอื่น **ไม่จำเป็นต้องติดตั้ง Python** ก็สามารถรันตัวจำลองเหตุการณ์ได้ทันที
- **Native Test Mode Support (`--test` / `NEKO_TEST_MODE=1`):** ข้ามการตรวจจับ Process ของเกม (`pso2.exe`), File Handle, Timestamp Skew, และ Velocity Limit สำหรับเครื่องที่ไม่มีตัวเกม PSO2 NGS ทำให้ทดสอบยอด Meseta และส่งข้อมูลขึ้นคลาวด์ได้ 100%
- **Smart Sample Log Ingestion:** เมื่อเปิดโฟลเดอร์ `sample_logs` หรือไฟล์ทดสอบ ระบบจะอ่านและประมวลผลข้อมูลตั้งแต่บรรทัดแรกทันที ไม่ข้ามไปยังท้ายไฟล์
- **แก้ไขปุ่มพับจอ (Window Minimize Fix):** ปรับปรุง Event Loop ดักจับสถานะ `<Map>` ขณะ Minimize ให้หน้าต่างย่อลง Taskbar ได้อย่างสมบูรณ์ ไม่เด้งกลับขึ้นมาเอง
- **1-Click Test Runners:**
  - `NEKO Tracker (Test Mode)` — ทางลัดบน Desktop/Start Menu เปิดโปรแกรมในโหมดทดสอบทันที
  - `Quick_Test_All_In_One.bat` — รัน Mock Simulator สตรีมข้อมูลสด + เปิด NekoTracker
  - `Run_Test_Mode.bat` — รัน NekoTracker ในโหมด Bypass ตรวจจับตัวเกม
  - `Start_Mock_Stream.bat` — เปิดหน้าต่าง Live Streamer จำลองการดรอปไอเทมและ Meseta ต่อเนื่อง
- **`sample_logs/`:** โฟลเดอร์ Log ตัวอย่างที่แนบไปพร้อมติดตั้ง สามารถคลิก "เลือกโฟลเดอร์ Log" แล้วเลือกโฟลเดอร์นี้เพื่อทดสอบได้ทันที

---

## 📖 วิธีการติดตั้งและทดสอบ (Installation & Testing Guide)

### 🇹🇭 ภาษาไทย (TH)

#### ก. การติดตั้งปกติ (สำหรับเล่นเกมจริง)
1. ดาวน์โหลดไฟล์ `NekoTracker-Setup-v7.1.0.exe`
2. ดับเบิลคลิกเพื่อเริ่มการติดตั้ง (ไม่ต้องกด Run as administrator)
3. กด Next เพื่อติดตั้งลงใน `%LOCALAPPDATA%\NEKO FAMILY\NekoTracker`
4. เมื่อติดตั้งเสร็จ สามารถเปิด **NEKO Item & Meseta Tracker** เพื่อใช้งานคู่กับการเล่นเกมจริงได้ทันที

#### ข. การทดสอบบนเครื่องเทส (ไม่มีเกมหรือไม่มี Python)
1. ติดตั้งตัวติดตั้ง `NekoTracker-Setup-v7.1.0.exe` ตามปกติ
2. สามารถเปิดทดสอบได้ 2 วิธี:
   - **วิธีที่ 1 (แนะนำ):** ดับเบิลคลิกทางลัด Desktop หรือ Start Menu: **`NEKO Tracker (Test Mode)`** แล้วคลิกเลือกโฟลเดอร์ `sample_logs`
   - **วิธีที่ 2:** คลิก **Quick Test All-in-One** บน Desktop/Start Menu เพื่อรัน Live Streamer ร่วมกับตัวโปรแกรม
3. สังเกตชื่อตัวละคร `Vale3neko`, ยอดเงิน Meseta วิ่งขึ้นสด, ไอเท็มดรอป, และทดสอบหน้าต่าง Overlay และ ARKS War Room ได้ทันที

---

### 🇬🇧 English (EN)

#### A. Standard Installation (For Live Gameplay)
1. Download `NekoTracker-Setup-v7.1.0.exe`.
2. Double-click the installer (no admin elevation required).
3. Proceed with the setup wizard to install into `%LOCALAPPDATA%\NEKO FAMILY\NekoTracker`.
4. Launch **NEKO Item & Meseta Tracker** to track your live NGS farming session.

#### B. Testing on Clean / Non-Game Machines
1. Run `NekoTracker-Setup-v7.1.0.exe` and complete installation.
2. In the Windows Start Menu, open the **NEKO Item & Meseta Tracker** folder.
3. Click **Quick Test All-in-One** (or run `Quick_Test_All_In_One.bat` in the app directory).
4. The background mock streamer will generate simulated drops automatically.
5. In NekoTracker, click **"Select Log Folder"** and pick the bundled `sample_logs` folder.
6. Verify live Meseta counters, M/hr rate, item drops, and test the Gadget Overlay mode.
