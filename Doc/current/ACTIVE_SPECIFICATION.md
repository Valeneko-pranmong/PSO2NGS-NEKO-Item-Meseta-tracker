# 🌸 NEKO Item & Meseta Tracker — Active System Specification (สเปคระบบปัจจุบัน)

> **สถานะ:** `[CURRENT]` 🟢 — เอกสารสเปคทางเทคนิคหลักของระบบ (Active Production Source of Truth)  
> **รุ่นปัจจุบัน:** Python Version `6.1.0` / C# WPF Version `7.0.0-alpha`  
> **ทีมพัฒนา:** NEKO FAMILY TEAM SHIP 4 JP / Vale3neko  

---

## 1. ภาพรวมระบบ (System Overview)

NEKO Item & Meseta Tracker เป็นเครื่องมือติดตามข้อมูลการฟาร์ม N-Meseta และไอเทมดรอปแบบ Real-time สำหรับเกม **Phantasy Star Online 2: New Genesis (PSO2:NGS)** โดยเฉพาะช่วง PSE Burst ฟาร์มเงินและแคปซูล 

ระบบถูกแบ่งออกเป็น 2 สถาปัตยกรรมหลัก:
1. **Python Tracker (V6.1.0):** สถาปัตยกรรม Modular ระบบเดิมที่ขับเคลื่อนด้วย CustomTkinter, EventBus และผสานเข้ากับโหมด **ARKS War Room** ส่ง Telemetry แบบสดขึ้น Google Firebase Realtime Database
2. **C# WPF Native Tracker (V7.0.0-alpha):** สถาปัตยกรรมเนทีฟ Windows .NET 6 WPF ที่เน้นประสิทธิภาพระดับสูง การเรนเดอร์กราฟิกฮาร์ดแวร์เร่งความเร็ว และมีระบบความปลอดภัย **AntiTamperGuard**

---

## 2. สถาปัตยกรรม Python Tracker (V6.1.0)

### 2.1 ระบบตรวจจับไฟล์และการประมวลผล ActionLog (Log Ingestion Pipeline)
* **การตรวจจับตำแหน่งไฟล์:** ตรวจหาโฟลเดอร์อัตโนมัติที่ `Documents\SEGA\PHANTASYSTARONLINE2\log_ngs` พร้อมให้ผู้ใช้สามารถเลือกโฟลเดอร์ผ่าน File Dialog ได้
* **การเลือกไฟล์ล่าสุด:** คัดเลือกไฟล์ที่มีชื่อขึ้นต้นด้วย `ActionLog*.txt` และมีค่า `getmtime` ล่าสุด
* **การระบุ Encoding อัตโนมัติ:** ตรวจสอบ BOM ไบต์ต้นไฟล์เพื่อรองรับ `utf-16` (LE), `utf-16-be`, `utf-8-sig`, และ `utf-8`
* **การอ่านไฟล์แบบไม่สะดุด (Seek-based Ingestion):** จัดเก็บค่า `last_file_pos` และอ่านเฉพาะบรรทัดใหม่ที่ถูกเขียนต่อท้ายโดยตัวเกมใน Background Thread (`monitor_log_file`) ทุก 1 วินาที

### 2.2 โลจิกการประมวลผลข้อความและข้อมูลการเงิน (Log Parsing Engine)
* **การตรวจจับตัวละคร (Zero-Login Operative Detection):**
  - วิเคราะห์โครงสร้าง Tab-delimited: `Timestamp \t Seq \t [Action] \t PlayerID \t CharacterName \t ...`
  - ตรวจสอบว่าคอลัมน์ลำดับที่ 3 เป็นตัวเลข PlayerID (`parts[3].isdigit()`) และดึงชื่อตัวละครจริงจากคอลัมน์ลำดับที่ 4 (`parts[4]`)
  - ใช้ชื่อตัวละครจริงในเกมเป็น **Primary Key** ของระบบ ไม่ต้องมีฟอร์ม Login ไม่ต้องกรอกชื่อผู้ใช้หรือรหัสผ่าน
  - ยิง Event `character_detected` ไปยังระบบ EventBus ทันที
* **การคำนวณเงิน N-Meseta:**
  - Regular Expressions:
    - ตรวจจับยอดเงินที่ดรอป: `\t(?:N-)?Meseta\s*\(\s*(\d+)\s*\)`
    - ตรวจจับยอดเงินในกระเป๋า: `\tCurrent(?:N-)?Meseta\s*\(\s*(\d+)\s*\)`
  - ตรวจจับการกระทำที่ถูกต้อง (Valid Actions): `[Pickup]`, `[AutoSell]`, `[Reward]`, `[Clear]`
  - คำนวณรายได้สุทธิ (Net Income) จากผลต่างของ `CurrentMeseta` เมื่อยอดเงินเพิ่มขึ้น และนำไปคำนวณอัตราความเร็ว **Meseta per Hour (M/hr)**
* **การติดตามจำนวนไอเทมดรอป:**
  - ตรวจจับรูปแบบ `\t([^\t]+)\tNum\((\d+)\)` สะสมเข้าสู่ `item_counts` ดิกชันนารี
  - รองรับระบบ **Watchlist Filter** เพื่อเลือกกรองเฉพาะไอเทมที่สนใจ

### 2.3 ระบบ EventBus (Decoupled Pub/Sub Architecture)
ระบบใช้ตัวกระจายเหตุการณ์ภายใน (`modules/event_bus.py`) เพื่อแยก Logic ออกจาก UI อย่างเด็ดขาด:
* `meseta_earned(amount, wallet)`: แจ้งเตือนเมื่อได้รับเงิน Meseta
* `tracker_reset()`: แจ้งเตือนเมื่อผู้ใช้กดรีเซ็ตเซสชัน
* `character_detected(character_name, player_id)`: แจ้งเตือนเมื่อพบตัวละครใหม่
* `board_coord_changed(coord, sector_x, sector_y, slot)`: แจ้งเตือนเมื่อมีการเปลี่ยนพิกัดเป้าหมาย
* `war_telemetry_synced(character_name, meseta, sector_coord)`: แจ้งเตือนเมื่อข้อมูลถูกซิงค์

### 2.4 โหมด ARKS War Room & ระบบพิกัด Sector + 4 Slots
* **พิกัดอวกาศแบบ Sector และ Quadrant Sub-cells:**
  - แกน X (Sector X): ช่วงค่าระหว่าง `-12` ถึง `+25` (รวม 38 ช่องในแนวนอน)
  - แกน Y (Sector Y): ช่วงค่าระหว่าง `-11` ถึง `+9` (รวม 21 ช่องในแนวตั้ง)
  - รวมทั้งหมด: 798 Sectors ทั่วกาแล็กซี ARKS
  - **4 Sub-cell Slots ต่อ Sector:**
    - ช่อง `#1` (NW - บนซ้าย): เป้าหมาย 25,000,000 N-Meseta
    - ช่อง `#2` (NE - บนขวา): เป้าหมาย 25,000,000 N-Meseta
    - ช่อง `#3` (SW - ล่างซ้าย): เป้าหมาย 25,000,000 N-Meseta
    - ช่อง `#4` (SE - ล่างขวา): เป้าหมาย 25,000,000 N-Meseta
    - รวมเป้าหมายทั้ง Sector: 100,000,000 N-Meseta
* **ระบบแปลพิกัดอัจฉริยะ (Coordinate Parser):**
  รองรับการป้อนพิกัด 7 รูปแบบที่พบได้จากการคัดลอกบนหน้าเว็บและอินพุตของผู้ใช้:
  1. ตัวเลข 3 จำนวน: `"0, 0, 1"`, `"3, 3, 4"`
  2. รูปแบบ Hash: `"0,0#1"`, `"3, 3 # 4"`
  3. รูปแบบ Bracket: `"[0, 0, 1]"`, `"[3, 3, 4]"`
  4. JSON Dict/String: `{"x": 0, "y": 0, "slot": 1}`, `{"sector_x": 3, "sector_y": 3, "slot": 4}`
  5. ข้อความคัดลอกจาก Web UI: `"คัดลอกพิกัด [8, -2] ช่อง #3 ไปใส่ในโปรแกรม"`
  6. รูปแบบทิศทาง Quadrant: `"0, 0 NW"`, `"0, 0 บนซ้าย"`
  7. Fallback 2 จำนวน: `"0, 0"`, `"[15, -8]"` (จะกำหนดช่องเริ่มต้นเป็น Slot 1)
* **Realtime Sync Worker:**
  - Background Thread ทำงานอัตโนมัติ มี Debounce 0.35 วินาที เพื่อรวบยอดคำขอซิงค์ และส่ง Heartbeat ทุก 5.0 วินาที
  - ส่งข้อมูลไปยัง Google Firebase Realtime Database ตาม Wire Contract
  - สำรองข้อมูลสถานะออฟไลน์ลงไฟล์ `%APPDATA%\NekoTrackerOffline\war_stats.json` และไดเรกทอรีโลคอล `E:\ARKS War Room`

### 2.5 โหมดการแสดงผล (User Interfaces)
* **Main Dashboard:** แสดงยอดเงิน, อัตรา M/hr, เวลาที่ฟาร์ม, รายการไอเทม, และปุ่มลัดสลับโหมด
* **ARKS War View:** แสดงพิกัด Sector ปัจจุบัน, ช่อง Quadrant ที่กำลังยึด, เปอร์เซ็นต์ความคืบหน้า, ชื่อ Operative, และสถานะการซิงค์สด
* **Gadget Mode (Overlay):**
  - **Full Overlay:** แสดงทั้งรายได้ N-Meseta และรายการไอเทมดรอปล่าสุด
  - **Mini Overlay:** แสดงเฉพาะตัวเลขเงิน Meseta ในขนาดกะทัดรัด โปร่งใส ลอยอยู่เหนือหน้าจอเกม

---

## 3. สถาปัตยกรรม C# WPF Native Tracker (V7.0.0-alpha)

ไดเรกทอรี [`NekoTracker-WPF/`](../../NekoTracker-WPF/) และ [`NekoTracker.Tests/`](../../NekoTracker.Tests/) บรรจุซอร์สโค้ดของเนทีฟแอปพลิเคชัน Windows .NET 6 WPF:
* **AntiTamperGuard (`Security/AntiTamperGuard.cs`):** ตรวจจับการแทรกแซงตัวโปรแกรม, การดัดแปลงตัวแปรในหน่วยความจำ, และตรวจสอบความถูกต้องของ Process
* **ActionLogParser (`Core/ActionLogParser.cs`):** ตัวอ่าน ActionLog ประสิทธิภาพสูง แปลงข้อมูลเป็น `ActionLogRecord` โครงสร้าง Strong-typed
* **LogWatcher (`Core/LogWatcher.cs`):** เฝ้ามองการเปลี่ยนแปลงของไฟล์ Log ในเครื่องแบบ Event-driven
* **LanguageManager (`Localization/LanguageManager.cs`):** ระบบรองรับหลายภาษา (อังกฤษ `en`, ญี่ปุ่น `ja`, ไทย `th`) โดยโหลดจาก JSON Embedded Resource
* **PastelTheme (`Themes/PastelTheme.xaml`):** สไตล์หน้าตา UI มินิมอล โทนสีชมพูพาสเทลเอกลักษณ์ของ NEKO Family

---

## 4. มาตรฐานความปลอดภัย (Security & Compliance)

1. **100% TOS Safe (เป็นไปตามข้อตกลงผู้ใช้งาน):** อ่านเฉพาะไฟล์ Text Log ที่ตัวเกมสร้างขึ้นในโฟลเดอร์ Documents เท่านั้น ไม่มีการยุ่งเกี่ยวกับหน่วยความจำเกม (RAM) ไม่มีการ Hook API หรือฉีด DLL ใดๆ
2. **Zero-Login Architecture:** ปลอดภัยสูงสุดด้วยการไม่ร้องขอ ไม่จัดเก็บ และไม่ส่งรหัสผ่านใดๆ ตัวตน Operative ผูกกับชื่อตัวละครที่ตรวจพบจาก Log โดยตรง
3. **Fail-Safe Offline Mode:** หากไม่มีการเชื่อมต่ออินเทอร์เน็ต ระบบจะยังคงทำหน้าที่เป็น Offline Tracker ที่สมบูรณ์แบบได้ 100% โดยไม่มีข้อจำกัด
