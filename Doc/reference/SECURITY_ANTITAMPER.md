# 🛡️ NEKO Item & Meseta Tracker — Security & Anti-Tamper Specification (ความปลอดภัยและการป้องกันการแทรกแซง)

> **สถานะ:** `[REFERENCE]` 🔵 — เอกสารอ้างอิงมาตรฐานความปลอดภัยและการปฏิบัติตามกฎเกม (Security & Compliance Reference)  
> **ขอบเขต:** อธิบายหลักการ 100% TOS Safe, สถาปัตยกรรม Zero-Login, และระบบป้องกันการโกง `AntiTamperGuard`  

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
[NEKO Tracker (Python / C# WPF)]
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

## 3. สถาปัตยกรรม `AntiTamperGuard` (C# .NET 6 WPF)

ในโปรเจกต์เวอร์ชัน C# WPF ([`NekoTracker-WPF/Security/`](../../NekoTracker-WPF/Security/)) มีการติดตั้งระบบ **AntiTamperGuard** เพื่อรับประกันความถูกต้องของข้อมูลสถิติและการทำงาน:

### 3.1 คุณสมบัติการตรวจสอบ (Integrity Validations)
1. **Process Integrity Validation (`IProcessValidator`):** ตรวจสอบว่า Process ที่กำลังรันเป็นไบนารีที่ถูกต้อง ไม่ถูก Debugger แปลกปลอม Hook หรือมีกระบวนการ Memory Tampering
2. **Log File Lock & Stream Validation:** ตรวจสอบว่าไฟล์ Log ที่กำลังอ่านถูกสร้างและถือครอง Handle โดยไฟล์ระบบของ Windows จริง ไม่ใช่ไฟล์จำลองที่ถูกเขียนขึ้นเพื่อปั่นตัวเลขสถิติ
3. **Abnormal Income Rate Detection:** ตรวจจับอัตราการเพิ่มของเงิน Meseta ที่ผิดธรรมชาติ (เช่น เพิ่มขึ้นหลายร้อยล้านในเสี้ยววินาที) เพื่อป้องกันการส่งข้อมูลเท็จขึ้นระบบ War Room
4. **Decoupled Architecture for Unit Testing:** มีการใช้อินเตอร์เฟซ `IProcessValidator` เพื่อรองรับการทำ Mock ในชุดทดสอบ Unit Test ([`NekoTracker.Tests/AntiTamperTests.cs`](../../NekoTracker.Tests/AntiTamperTests.cs)) ทำให้มั่นใจได้ว่าระบบทำงานถูกต้อง 100%
