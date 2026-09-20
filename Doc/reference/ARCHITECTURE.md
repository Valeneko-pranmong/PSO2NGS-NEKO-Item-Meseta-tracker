# 🏛️ NEKO Item & Meseta Tracker — System Architecture (สถาปัตยกรรมระบบ)

> **สถานะ:** `[REFERENCE]` 🔵 — เอกสารอ้างอิงสถาปัตยกรรมทางเทคนิค (Technical Architecture Reference)  
> **ขอบเขต:** อธิบายการไหลของข้อมูล (Data Pipelines), การออกแบบ Multi-threading, และระบบกระจายเหตุการณ์ (EventBus)  

---

## 1. ผังสถาปัตยกรรมระดับสูง (High-Level Architecture)

```
+-----------------------------------------------------------------------------------+
|                            PSO2:NGS Game Client                                   |
|   (Runs independently - Writes combat, pickup, and economy logs to Windows disk)  |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          | Appends text lines (UTF-16/UTF-8)
                                          v
+-----------------------------------------------------------------------------------+
|                 Local File System: Documents/SEGA/.../ActionLog_*.txt             |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          | Non-invasive Seek & Read (TOS 100% Safe)
                                          v
+-----------------------------------------------------------------------------------+
|                        NEKO TRACKER INGESTION PIPELINE                            |
|                                                                                   |
|   [Background Monitor Thread] (Polls every 1s, maintains last_file_pos)           |
|                                         |                                         |
|                                         v                                         |
|   [Log Parsing Engine]                                                            |
|     * Zero-Login Regex: Detects PlayerID & In-Game Character Name                 |
|     * Meseta Calculator: Parses [Pickup], [AutoSell], CurrentMeseta delta         |
|     * Item Counter: Extracts item name & quantity from Num(N)                     |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          | Emits decoupled domain events
                                          v
+-----------------------------------------------------------------------------------+
|                     INTERNAL EVENT BUS (modules/event_bus.py)                     |
|                                                                                   |
|   * character_detected(name, id)        * meseta_earned(amount, wallet)           |
|   * tracker_reset()                     * board_coord_changed(coord, slot)        |
|   * war_telemetry_synced(payload)                                                 |
+-------------------+-------------------------------------+-------------------------+
                    |                                     |
                    v                                     v
+-----------------------------------+   +-------------------------------------------+
|          UI PRESENTATION          |   |          ARKS WAR MODE SUBSYSTEM          |
|                                   |   |                                           |
|  * Main Dashboard (dashboard_ui)  |   |  * WarService (modules/war_mode)          |
|  * Gadget Overlay (Full & Mini)   |   |  * Smart Coordinate Parser (TargetCoord)  |
|  * Watchlist Filter System        |   |  * Background Sync Worker (Debounce 0.35s)|
|  * War Dashboard (war_view)       |   |  * Local Backup: war_stats.json           |
+-----------------------------------+   +---------------------+---------------------+
                                                              |
                                                              | Sends telemetry via REST/Admin
                                                              v
                                        +-------------------------------------------+
                                        |      Google Firebase Realtime Database    |
                                        |                                           |
                                        |  * /arks_war_room/operatives/{char_name}  |
                                        |  * /arks_war_room/sectors/{coord}/slots   |
                                        |  * /arks_war_room/activity_feed           |
                                        +-------------------------------------------+
```

---

## 2. ท่อประมวลผลข้อมูล (Data Ingestion & Event Pipeline)

### ขั้นที่ 1: การเฝ้าสังเกตและอ่านไฟล์ Log (File Ingestion)
1. เธรด `monitor_log_file` เริ่มต้นทำงานในโหมด `daemon=True`
2. เรียกฟังก์ชัน `find_latest_log_file()` เพื่อสแกนหาไฟล์ `ActionLog*.txt` ที่มี Timestamp ล่าสุด
3. ตรวจจับการเข้ารหัสไฟล์ (BOM Header) เพื่อตั้งค่า `active_encoding` อย่างถูกต้อง
4. เปิดไฟล์ในโหมด `r` และย้าย pointer ไปยังจุดสิ้นสุดเดิม (`f.seek(last_file_pos)`) ป้องกันการอ่านข้อมูลซ้ำ

### ขั้นที่ 2: การแยกชิ้นส่วนข้อความ (Line Parsing)
1. **การตรวจจับตัวละคร:**
   ```
   2026-09-20T14:30:15\t1024\t[Pickup]\t10884920\tVale3neko\t...
   ```
   คอลัมน์ลำดับที่ 3 คือ `PlayerID` (`10884920`) และคอลัมน์ลำดับที่ 4 คือ `CharacterName` (`Vale3neko`)
   ระบบจะอัปเดต `self.character_name` และยิง Event `character_detected`
2. **การตรวจจับยอดเงิน N-Meseta:**
   ค้นหาด้วย Regular Expressions:
   - รายได้จากกล่อง/มอนสเตอร์: `\t(?:N-)?Meseta\s*\(\s*(\d+)\s*\)`
   - ยอดเงินสุทธิในกระเป๋า: `\tCurrent(?:N-)?Meseta\s*\(\s*(\d+)\s*\)`
   เมื่อตรวจพบ `CurrentMeseta` มีค่าเพิ่มขึ้น ระบบจะคำนวณ `income = new_wallet - current_wallet` และยิง Event `meseta_earned`

### ขั้นที่ 3: การกระจายเหตุการณ์ผ่าน EventBus
* โมดูลต่างๆ ไม่จำเป็นต้องรู้จักกันโดยตรง (Decoupled Architecture)
* `WarService` สมัครรับข้อมูลจาก Event `meseta_earned` เพื่อสะสมเงินเข้าช่องพิกัดที่กำลังยึด
* หน้าต่าง UI (`DashboardFrame`, `OverlayWindow`, `WarDashboardFrame`) อัปเดตตัวเลขแสดงผลผ่าน Event หรือตัวแปรสถานะอย่างปลอดภัย

### ขั้นที่ 4: การส่ง Telemetry แบบ Real-time
* เมื่อมี Event การเงินเข้ามา `WarService` จะสะสมยอดเข้า `session_contribution`
* สั่ง Trigger ตัวจับเวลา Debounce (0.35 วินาที) ของ `_realtime_sync_worker`
* เมื่อหมดเวลารวมคำขอ Worker Thread จะส่งคำขอ HTTP PUT/PATCH ไปยัง Firebase Realtime Database
* เมื่อสำเร็จจะยิง Event `war_telemetry_synced` กลับมายัง UI เพื่อแสดงไฟสถานะสีเขียว

---

## 3. ความปลอดภัยของเธรด (Thread Safety Model)

เนื่องจากระบบมีทั้ง Main UI Thread และ Background Worker Threads จึงมีการใช้ Synchronization Primitives ดังนี้:
1. `data_lock (threading.Lock)`: อยู่ใน `NGSTrackerApp` ใช้ล็อกการเข้าถึง `session_meseta`, `current_wallet`, `item_counts`, และตัวจับเวลาเวลาดรอป
2. `_sync_lock (threading.Lock)`: อยู่ใน `WarService` ใช้ล็อกการอ่านและเขียนข้อมูล Telemetry ที่กำลังส่งขึ้นเซิร์ฟเวอร์
3. `_sync_event (threading.Event)`: ใช้ส่งสัญญาณกระตุ้น Background Sync Worker โดยไม่ต้องรัน Spin-wait Loop ช่วยลดการใช้ CPU ให้เหลือใกล้เคียง 0%
