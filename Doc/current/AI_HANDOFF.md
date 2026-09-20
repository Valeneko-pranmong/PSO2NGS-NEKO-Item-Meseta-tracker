# 🤖 NEKO Item & Meseta Tracker — AI & Engineering Handoff (คู่มือการส่งต่องาน)

> **สถานะ:** `[CURRENT]` 🟢 — เอกสารส่งต่องานเชิงปฏิบัติการสำหรับ AI Agents และวิศวกรซอฟต์แวร์  
> **เป้าหมาย:** สรุปกฎระเบียบ สภาพแวดล้อม คำสั่งทดสอบ และข้อควรระวังสำคัญสำหรับการพัฒนาต่อยอด  

---

## 🛠️ สภาพแวดล้อมและเครื่องมือที่จำเป็น (Toolchain & Environment)

* **ระบบปฏิบัติการ:** Windows 10 / Windows 11 (64-bit)
* **Python Runtime:** Python 3.11.x (แนะนำ 3.11.16)
  - แพ็กเกจหลัก: `customtkinter`, `Pillow`, `pytest`, `pytest-mock`, `pytest-asyncio`
  - ตัวจัดการแพ็กเกจ: `pip` หรือ `uv`
* **Build Tools (อุปกรณ์เสริมสำหรับการทำตัวติดตั้ง):** Inno Setup 6 (ISCC.exe), PyInstaller

---

## 🚀 คำสั่งหลักสำหรับการทำงาน (Operational Commands)

### 1. การรันแอปพลิเคชัน Python (V7.1.0)
```bash
# รันผ่านคำสั่ง Python
python meseta_tracker.py

# หรือรันผ่าน Batch Script บน Windows
run_app.bat
```

### 2. การรันชุดทดสอบ Python (Unit & Integration Tests)
```bash
# รันด้วย pytest แบบละเอียด
python -m pytest -v

# หรือรันผ่าน Batch Script
run_test.bat
```
> **เกณฑ์การยอมรับ:** ผลการทดสอบต้องผ่านทั้งหมด **24 / 24 รายการ (100% Passed)**

### 3. การคอมไพล์และสร้างชุดติดตั้ง Windows (Installer Build Pipeline)
```bash
# รันผ่านสคริปต์อัตโนมัติ (ทดสอบ Python -> แพ็กเกจ PyInstaller -> สร้าง Setup.exe -> Smoke Test)
python installer/build_installer.py

# หรือรันผ่าน Batch Script บน Windows
build_installer.bat
```
> **ผลลัพธ์:** ไฟล์ติดตั้ง `artifacts/release-v6.1.0/NekoTracker-Setup-v6.1.0.exe` พร้อมค่าแฮช `SHA256SUMS.txt`  
> **มาตรฐาน:** ถอดแบบตามมาตรฐานกลาง [`Doc/reference/INSTALLER_STANDARD.md`](../reference/INSTALLER_STANDARD.md) (Per-User `%LOCALAPPDATA%\NEKO FAMILY\NekoTracker`, Non-elevated `PrivilegesRequired=lowest`, บล็อก non-x64, และตัวโปรแกรมหลักคือ Python Tracker)

---

## 🧭 แผนผังโค้ดและจุดเชื่อมต่อสำคัญ (Code Map & Entrypoints)

| ส่วนประกอบ | ไฟล์หลัก | หน้าที่และความรับผิดชอบ |
| :--- | :--- | :--- |
| **Main Python App** | `meseta_tracker.py` | หน้าต่างหลัก (`NGSTrackerApp`), Thread ตรวจจับไฟล์ Log, ตัวดักจับข้อความ N-Meseta และไอเทม |
| **Global Config** | `config.py` | พาธไฟล์, ค่าสีธีมพาสเทล, การโหลดฟอนต์ระบบ (Sarabun/Kanit), ค่าคงที่พิกัดและ Firebase |
| **Offline UI** | `dashboard_ui.py`<br>`overlay_ui.py` | แดชบอร์ดสรุปรายได้ต่อชั่วโมง, รายการไอเทม, และหน้าต่างลอยทับหน้าจอเกม (Full/Mini) |
| **Internal EventBus** | `modules/event_bus.py` | ระบบกระจาย Event ภายใน เพื่อตัดการผูกติด (Decoupling) ระหว่าง UI และ Business Logic |
| **ARKS War Subsystem** | `modules/war_mode/war_service.py`<br>`modules/war_mode/war_view.py` | จัดการข้อมูล Telemetry, คลาส `TargetCoord`, Smart Coordinate Parser, Background Sync Worker |
| **Firebase Broadcaster** | `tools/firebase_war_sync.py` | ตัวส่งข้อมูลขึ้น Google Firebase Realtime Database รองรับทั้ง Admin SDK และ REST Fallback |
| **Installer Pipeline** | `installer/build_installer.py`<br>`installer/NekoTracker.iss`<br>`installer/README.md`<br>`build_installer.bat` | ระบบคอมไพล์และสร้างชุดติดตั้ง Windows (Inno Setup 6) ตามมาตรฐานกลาง พร้อมทดสอบ Process Smoke อัตโนมัติ |
| **Distribution Artifacts** | `artifacts/release-v6.1.0/` | โฟลเดอร์เก็บอาร์ติแฟกต์ทางการ (`NekoTracker-Setup-v6.1.0.exe`, `SHA256SUMS.txt`, `README.md`) |
| **Archived Auth** | `archive/legacy_auth/` | **[ห้ามแตะต้อง]** ซอร์สโค้ดระบบล็อกอินเดิมที่ปลดระวางแล้ว ห้ามนำกลับมา import เด็ดขาด |
| **Archived WPF** | `archive/legacy_wpf/` | **[ห้ามแตะต้อง]** ซอร์สโค้ดเนทีฟ C# WPF และชุดทดสอบที่ยกเลิกการพัฒนาแล้ว ห้ามนำมาบิลด์ใน Production |

---

## ⚠️ กฎเหล็กและข้อห้ามเด็ดขาด (Invariants & Guardrails)

1. **Zero-Login Architecture:**
   - **ห้ามสร้างฟอร์ม Login, ห้ามถาม Username หรือ Password จากผู้ใช้เด็ดขาด**
   - ตัวตนของ Operative จะต้องดึงมาจากชื่อตัวละครจริงในเกมผ่านไฟล์ `ActionLog` อัตโนมัติ (`Timestamp \t Seq \t [Action] \t PlayerID \t CharacterName ...`)
2. **ขอบเขตพิกัด Sector และ Quadrant Slots:**
   - พิกัด Sector X ต้องอยู่ในช่วง `[-12, +25]`
   - พิกัด Sector Y ต้องอยู่ในช่วง `[-11, +9]`
   - หมายเลขช่อง Slot ต้องอยู่ในช่วง `[1, 4]` (1: NW บนซ้าย, 2: NE บนขวา, 3: SW ล่างซ้าย, 4: SE ล่างขวา)
   - ยอดเงินเป้าหมาย: ช่องละ `25,000,000` N-Meseta, รวมทั้ง Sector `100,000,000` N-Meseta
3. **100% TOS Safe (ห้ามแทรกแซงตัวเกม):**
   - ห้ามเขียนโค้ดที่แตะต้อง Process หน่วยความจำของเกม หรือ Hook Windows APIs ไปยังไคลเอนต์เกม PSO2:NGS
   - อ่านข้อมูลผ่าน Stream/Seek ของไฟล์ข้อความในดิสก์เท่านั้น
4. **ความปลอดภัยของเธรด (Thread Safety):**
   - ใน `meseta_tracker.py` ตัวแปรเกี่ยวกับเงินและไอเทมถูกป้องกันด้วย `self.data_lock`
   - ใน `war_service.py` การซิงค์และสถานะ Telemetry ถูกป้องกันด้วย `self._sync_lock`
   - การอัปเดต UI จาก Worker Thread ต้องสั่งผ่าน EventBus หรือ Tkinter `self.after` / Dispatcher เสมอ
