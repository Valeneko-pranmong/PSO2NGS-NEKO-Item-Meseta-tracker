# 📦 NEKO Item & Meseta Tracker — Windows Installer Pipeline

> **สถานะ:** `[CURRENT]` 🟢 — ระบบคอมไพล์และสร้างชุดติดตั้งทางการของ NEKO FAMILY  
> **มาตรฐานอ้างอิง:** [`Doc/reference/INSTALLER_STANDARD.md`](../Doc/reference/INSTALLER_STANDARD.md)  
> **รูปแบบตัวติดตั้ง:** Single-EXE Setup Wizard ขับเคลื่อนด้วย **Inno Setup 6** (LZMA2/Ultra64 Solid Compression)

---

## 🛠️ โครงสร้างไฟล์ในโฟลเดอร์นี้

| ไฟล์ | หน้าที่และความรับผิดชอบ |
| :--- | :--- |
| **`NekoTracker.iss`** | สคริปต์หลัก Inno Setup 6 กำหนดค่าตำแหน่งติดตั้ง (`%LOCALAPPDATA%\NEKO FAMILY\NekoTracker`), การบีบอัด, ชอร์ตคัต Desktop/Start Menu, และคำสั่งถอนการติดตั้ง |
| **`build_installer.py`** | สคริปต์ควบคุมการบิลด์อัตโนมัติ (Automated Build Orchestrator): รัน Test Suite -> แพ็ก Python App (PyInstaller) -> คอมไพล์ Setup.exe -> คำนวณ SHA-256 -> ทำ Lifecycle & Process Smoke Test |
| **`LICENSE.txt`** | ข้อกำหนดและสัญญาอนุญาตการใช้งานสำหรับแสดงในตัวติดตั้ง |
| **`../build_installer.bat`** | ไฟล์ Batch Script สำหรับสั่งบิลด์ตัวติดตั้งได้อย่างสะดวกรวดเร็วด้วยการดับเบิลคลิกเดียว |

---

## 🚀 คำสั่งการใช้งาน (Operational Commands)

### 1. การบิลด์แบบครบวงจร (Full Pipeline: Tests + Build + Smoke)
```bash
# รันผ่านคำสั่ง Python
python installer/build_installer.py

# หรือรันผ่าน Batch Script บน Windows
build_installer.bat
```

### 2. ตัวเลือกคำสั่งขั้นสูง (Advanced CLI Flags)
```bash
# ข้ามขั้นตอน Pre-flight Tests (รวดเร็วสำหรับการทดสอบตัวติดตั้ง)
python installer/build_installer.py --skip-tests

# ข้ามขั้นตอนการคอมไพล์ไฟล์ไบนารี (ใช้ผลลัพธ์เดิมใน dist/ และ build/ มาคอมไพล์ .iss)
python installer/build_installer.py --skip-build

# ข้ามขั้นตอน Process Smoke Test
python installer/build_installer.py --skip-smoke
```

---

## 📦 ผลลัพธ์จากการบิลด์ (Build Artifacts)

เมื่อกระบวนการเสร็จสิ้น ไฟล์ติดตั้งจะถูกสร้างขึ้นที่:
* **ไฟล์ตัวติดตั้ง:** `artifacts/release-v7.1.0/NekoTracker-Setup-v7.1.0.exe`
* **ไฟล์แฮชความปลอดภัย:** `artifacts/release-v7.1.0/SHA256SUMS.txt`

---

## 🛡️ กฎระเบียบและมาตรฐานความปลอดภัย (Invariants)

1. **Per-User Installation:** ติดตั้งที่ `%LOCALAPPDATA%\NEKO FAMILY\NekoTracker` โดยใช้ `PrivilegesRequired=lowest` เพื่อไม่ให้เด้ง UAC และไม่เสี่ยงต่อปัญหา Permission Denied
2. **Primary Application Integrity:** ตัวโปรแกรมหลักที่ติดตั้งคือ **Python Tracker V7.1.0 (พร้อมโหมด ARKS War Room & Multi-Language Support)** เสมอ
3. **Dedicated Test Suite for Clean Machines:** บรรจุ `tools/NekoLogSimulator.exe`, โฟลเดอร์ `sample_logs/`, และตัวเรียกทดสอบ `Quick_Test_All_In_One.bat` เพื่อให้เครื่องเทสอื่นทดสอบการทำงานได้ทันทีโดยไม่ต้องติดตั้ง Python หรือเปิดตัวเกม
4. **Fail-Closed:** หากมีชุดทดสอบใดๆ ล้มเหลว กระบวนการบิลด์จะหยุดทำงานทันที ไม่ปล่อยให้มีตัวติดตั้งที่มีบั๊กหลุดออกไป
