# 🛡️ NEKO Item & Meseta Tracker — Security & Anti-Tamper Specification (ความปลอดภัยและการป้องกันการแทรกแซง)

> **สถานะ:** `[REFERENCE]` 🔵 — เอกสารอ้างอิงมาตรฐานความปลอดภัยและการปฏิบัติตามกฎเกม (Security & Compliance Reference)  
> **ขอบเขต:** อธิบายหลักการ 100% TOS Safe, สถาปัตยกรรม Zero-Login, และระบบป้องกันการโกง `AntiTamperGuard` (Python V7.1.0 Native Subsystem)  

---

## 1. การปฏิบัติตามกฎเกณฑ์ของผู้ให้บริการเกม (100% TOS Safe)

โปรแกรม NEKO Tracker ถูกออกแบบขึ้นภายใต้หลักการความปลอดภัยสูงสุดเพื่อปกป้องบัญชีของผู้เล่น PSO2:NGS ทุกคน โดยปฏิบัติตามข้อกำหนดการให้บริการ (Terms of Service - TOS) ของบริษัท SEGA Corporation อย่างเคร่งครัด:

```
[PSO2:NGS Game Client]
        |
        | Official Game Logging Feature (SEGA Standard)
        v
[Windows File System: ActionLog_*.txt]
        ^
        | Passive Read-Only Stream (Non-invasive)
[NEKO Tracker (Python Engine)]
        |
        v
[AntiTamperGuard (7-Layer Verification)]
        |
        +---> Valid: Session Stats & ARKS War Room Sync
        |
        +---> Tampered: Discard Drop, Flag Compromised, Nullify Cloud Meseta (0)
```

### สิ่งที่โปรแกรม **ไม่ทำ** โดยเด็ดขาด:
1. **❌ ไม่มีการอ่านหน่วยความจำเกม (No Memory Reading):** ไม่มีการเรียกใช้ `OpenProcess`, `ReadProcessMemory`, หรือสแกน Memory Address ใดๆ ของเกม
2. **❌ ไม่มีการแทรกแซงโค้ด (No DLL Injection / API Hooking):** ไม่มีการฉีด DLL เข้าไปใน Process `pso2.exe` หรือแทรกแซง DirectX/Direct3D Render Pipeline
3. **❌ ไม่มีการดัดแปลงไฟล์เกม (No File Tampering):** ไม่แก้ไขไฟล์ `.pck`, `.ice`, หรือไฟล์ข้อมูลใดๆ ในโฟลเดอร์ติดตั้งเกม
4. **❌ ไม่มีการส่งคำสั่งจำลองการกดแป้น (No Macro / Automation):** ไม่มีฟังก์ชันบอท หรือการส่งปุ่มกดจำลองกลับไปยังตัวเกม

---

## 2. สถาปัตยกรรม Zero-Login (Zero-Login Identity Architecture)

เพื่อความเป็นส่วนตัวสูงสุดและป้องกันการรั่วไหลของข้อมูลรับรองตัวตน (Credentials):
* **ไม่มีฟอร์ม Login:** ผู้ใช้ไม่ต้องกรอกอีเมล ชื่อผู้ใช้ หรือรหัสผ่านใดๆ ทั้งสิ้น
* **ตรวจจับชื่อตัวละครอัตโนมัติ:** เมื่อผู้เล่นเข้าเกมและเก็บเงินหรือไอเทม ตัวเกมจะบันทึกบรรทัด ActionLog ที่มีรหัสผู้เล่นและชื่อตัวละคร (`Timestamp \t Seq \t [Action] \t PlayerID \t CharacterName ...`)
* **Primary Key ปลอดภัย:** ระบบใช้ชื่อตัวละครจริงในเกมเป็น Primary Key สำหรับการระบุตัวตนในสงคราม ARKS War Room ทำให้สามารถใช้งานได้ทันที 100% โดยไม่ต้องลงทะเบียน

---

## 3. ระบบรักษาความปลอดภัย AntiTamperGuard (Multi-Layer Heuristic Protection)

ในสถาปัตยกรรมหลักของ Python Tracker (V7.1.0) มีระบบป้องกันการแทรกแซงและการโกงข้อมูล `modules/security/anti_tamper.py` (`AntiTamperGuard`) ซึ่งทำงานตรวจสอบ Stream ของ ActionLog ผ่าน 9 เกราะป้องกันระดับสูง:

```
+-----------------------------------------------------------------------------------+
|                       AntiTamperGuard Verification Pipeline                       |
+-----------------------------------------------------------------------------------+
| Gate 0: Version Security Gating (is_version_secure, SemVer Check)                 |
| Gate 1: Game Process Verification (pso2.exe Toolhelp32 active check)              |
| Gate 2: Timestamp Verification (Clock skew < 60s, Replay < 5m, Non-rev)           |
| Gate 3: Sequence Monotonicity (seq increments, anomaly jump warning)              |
| Gate 4: Identity Consistency (Locked character name match)                        |
| Gate 5: Drop Limits & Sliding Window Velocity (Max 300k, 250k/min limit)          |
| Gate 6: Cadence Jitter Check (Statistical entropy / artificial timer detection)   |
| Gate 7: File Stream & Handle Verification (Restart Manager API game lock check)   |
| Gate 8: Canonical Path Gating (Official SEGA directory & symlink/junction check)  |
+-----------------------------------------------------------------------------------+
```

### 3.1 รายละเอียดของแต่ละเกราะป้องกัน (Verification Layers)
1. **Gate 0 — Version Security Gating (`INSECURE_CLIENT_VERSION`):**
   - ตรวจสอบความถูกต้องของ Semantic Versioning ด้วย `parse_semver` และ `compare_semver`
   - ปฏิเสธและเพิกถอนเวอร์ชันที่มีช่องโหว่ เช่น `7.0.0-alpha` หรือเวอร์ชันต่ำกว่า `MIN_SECURE_VERSION` (7.1.0)
2. **Gate 1 — Game Process Verification (`GAME_PROCESS_NOT_RUNNING`):**
   - ตรวจสอบผ่าน `WindowsProcessValidator` (ใช้ Win32 `Toolhelp32Snapshot` พร้อมแคช TTL 2 วินาที)
   - หากตรวจพบ ActionLog บันทึกเงินดรอปหรือไอเทมขณะที่ตัวเกม `pso2.exe` ไม่ได้รันอยู่ จะปฏิเสธบรรทัดนั้นและสแตมป์ว่าเป็นการฉีด Log ปลอม (Fake Log Injection)
3. **Gate 2 — Timestamp Verification (`TIMESTAMP_SKEW_OUT_OF_RANGE`, `TIMESTAMP_REPLAY_OLD`):**
   - ป้องกันเวลากระโดดไปในอนาคตเกิน `MAX_FUTURE_TIMESTAMP_SKEW_SEC` (60 วินาที)
   - ป้องกันการ Replay ข้อมูลเก่าย้อนหลังเกิน `MAX_PAST_TIMESTAMP_SKEW_SEC` (5 นาที)
   - ป้องกัน Timestamp ย้อนกลับหลังเกิน 2 วินาที
4. **Gate 3 — Sequence Monotonicity (`SEQUENCE_NUMBER_DECREASED`, `SEQUENCE_JUMP_ANOMALOUS`):**
   - Sequence ID ใน ActionLog ต้องเพิ่มขึ้นแบบ Monotonic หากค่าลดลงถือเป็นการแก้ไข Log ย้อนหลัง (Fatal)
   - หาก Sequence กระโดดผิดปกติเกิน 5,000 บรรทัด จะแจ้งเตือน Anomaly Warning (Non-fatal)
5. **Gate 4 — Identity Consistency (`CHARACTER_IDENTITY_MISMATCH`):**
   - ล็อกชื่อตัวละครในเซสชันผ่าน `lock_identity()` หากตรวจพบบรรทัดที่มีชื่อตัวละครอื่นแทรกเข้ามา จะปฏิเสธการนับเงิน
6. **Gate 5 — Drop Limits & Velocity Sliding Window (`DROP_AMOUNT_EXCEEDS_CEILING`, `VELOCITY_EXCEEDS_PHYSICAL_LIMIT`):**
   - **Single Drop Ceiling:** จำกัดเพดานเงินดรอปต่อครั้งสูงสุดที่ `300,000 N-Meseta` (ใน NGS ปกติไม่มีดรอปเกินนี้)
   - **Velocity Sliding Window:** คำนวณความเร็วแบบคิวย้อนหลัง 1 นาที จำกัดที่ `250,000 N-Meseta / นาที` (~15M/ชม. ซึ่งเป็นเพดานความเร็วฟาร์มสูงสุดทางกายภาพ)
7. **Gate 6 — Cadence Jitter Check (`ARTIFICIAL_BOT_CADENCE`):**
   - คำนวณค่าเบี่ยงเบนมาตรฐาน (Standard Deviation) ของช่วงเวลาระหว่างดรอปสะสมในคิว 15 ครั้ง
   - หากพบว่าช่วงเวลาคงที่และสม่ำเสมอเกินมนุษย์ (StdDev < 0.05 วินาที เช่น บอทตั้งเวลา `sleep(3.0)` คงที่) ระบบจะตรวจจับและสแตมป์ว่าเป็นการจำลองของบอท
8. **Gate 7 — File Handle & Game Ownership Check (`FILE_NOT_LOCKED_BY_GAME`, `UNAUTHORIZED_CONCURRENT_WRITER`):**
   - ใช้ Windows Restart Manager API (`rstrtmgr.dll`) ตรวจสอบว่าไฟล์ Log ปัจจุบัน **ถูกเปิดและถือครอง Write Handle โดย `pso2.exe` จริงหรือไม่**
   - หากเป็นไฟล์ที่แฮกเกอร์สร้างขึ้นเองหรือจำลองภายนอกที่ไม่มีเกมเปิดอยู่ จะติด `FILE_NOT_LOCKED_BY_GAME` ทันที
   - หากตรวจพบว่ามีโปรแกรมอื่นแอบเปิดไฟล์เขียนแทรกพร้อมกับตัวเกม จะติด `UNAUTHORIZED_CONCURRENT_WRITER`
9. **Gate 8 — Stream Continuity & Canonical Path Gating (`FILE_STREAM_TRUNCATED`, `NON_CANONICAL_LOG_PATH`):**
   - ตรวจจับขนาดไฟล์ Log หากขนาดไฟล์ลดลง (`current_size < last_size`) หรือตำแหน่ง Seek ย้อนกลับ
   - ตรวจสอบว่าโฟลเดอร์ Log อยู่ในไดเรกทอรีทางการของ SEGA (`Documents\SEGA\PHANTASYSTARONLINE2\log_ngs`) และไม่ใช่ NTFS Symlink หรือ Junction Point ปลอมแปลง

---

## 4. ผลลัพธ์เมื่อตรวจพบการแทรกแซง (Fail-Closed Enforcement)

เมื่อเกิดการละเมิดความปลอดภัยขั้นร้ายแรง (`is_fatal = True`):
1. **Local Tracker:** บรรทัดที่ถูกแทรกแซงจะไม่ถูกนำมาคำนวณเงินใน `session_meseta` และไอเทมจะไม่ถูกนับ
2. **Event Notification:** ยิง Event `tamper_violation` ผ่าน `EventBus` เพื่อแจ้งเตือนระบบที่เกี่ยวข้อง
3. **WarService Status:** สแตมป์สถานะ `is_tamper_compromised = True` และบันทึกคำเตือนลง `war_logs`
4. **Cloud Database Payload:**
   - ฟิลด์ `meseta` จะถูกปรับเป็น `0` ทันที
   - ฟิลด์ `security_status` จะแสดงเป็น `"TAMPER_COMPROMISED"` หรือ `"REVOKED_VERSION_INSECURE"`
   - ฟิลด์ `version_security_valid` จะกลายเป็น `False`
   - คำสั่ง `sync_to_cloud_database()` จะปฏิเสธการส่งข้อมูลขึ้น Cloud ทันทีเพื่อรักษาความโปร่งใสใน ARKS War Room
