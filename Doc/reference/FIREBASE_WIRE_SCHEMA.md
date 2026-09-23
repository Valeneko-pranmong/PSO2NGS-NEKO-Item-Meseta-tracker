# 📡 NEKO Item & Meseta Tracker — Firebase RTDB Wire Schema (โครงสร้างข้อมูล Firebase)

> **สถานะ:** `[REFERENCE]` 🔵 — สเปคข้อตกลงการแลกเปลี่ยนข้อมูลผ่านเครือข่าย (Network Wire Contract)  
> **ฐานข้อมูล:** Google Firebase Realtime Database (RTDB)  
> **URL เริ่มต้น:** กำหนดผ่านตัวแปรสภาพแวดล้อม (Private Endpoint)  
> **Root Namespace:** `arks_war_room`  

---

## 1. ภาพรวมการซิงค์ข้อมูล (Telemetry Synchronization Model)

โปรแกรม NEKO Tracker สื่อสารกับ Google Firebase Realtime Database ผ่าน 2 กลไก:
1. **Background Sync Worker ในตัวแอป:** อยู่ใน `WarService._realtime_sync_worker` ส่งข้อมูลอัตโนมัติผ่าน REST API (`urllib.request`) โดยมี Debounce 0.35 วินาที
2. **เครื่องมือ Standalone Broadcaster:** อยู่ใน `tools/firebase_war_sync.py` รองรับทั้ง Firebase Admin SDK (ด้วย Service Account JSON Key) และ REST Fallback

---

## 2. โครงสร้างเส้นทางข้อมูล (Database Path Architecture)

```
arks_war_room/
├── version_control/                  <-- ศูนย์ควบคุมเวอร์ชันและความปลอดภัยจากระยะไกล (Dynamic Remote Policy)
│   ├── latest_version: string ("7.1.0")
│   ├── min_secure_version: string ("7.1.0")
│   ├── revoked_versions: object { "7_0_0-alpha": true, "7_0_0": true }
│   ├── announcement: string
│   ├── download_url: string
│   └── last_updated: timestamp (ms)
├── operatives/
│   └── {character_name}/             <-- สถานะและสถิติตัวละครรายบุคคล (Cumulative across galaxy)
│       ├── character_name: string
│       ├── meseta: integer (0 หากเวอร์ชันไม่ปลอดภัย)
│       ├── raw_meseta: integer
│       ├── client_version: string ("7.1.0")
│       ├── version: string ("7.1.0")
│       ├── security_status: string ("SECURE" | "REVOKED_VERSION_INSECURE")
│       ├── version_security_valid: boolean
│       ├── farming_rate_mhr: integer (ความเร็วเงิน M/hr)
│       ├── farmingRateMhr: integer
│       ├── meseta_per_hour: integer
│       ├── sector_coord: object {x, y, slot}
│       ├── coord_key: string ("X,Y")
│       ├── slot: integer (1..4)
│       ├── slot_meseta: integer (ยอดเงินในช่องปัจจุบัน)
│       ├── raw_slot_meseta: integer
│       ├── sector_meseta: integer (ยอดเงินรวมทุกช่องใน Sector ปัจจุบัน)
│       ├── raw_sector_meseta: integer
│       ├── slot_farmed: object { "{X,Y}#{slot}": integer } (แผนที่เงินสะสมทุกช่องย่อย)
│       ├── session_meseta: integer
│       ├── total_farmed: integer
│       └── lastUpdated: timestamp (ms)
├── sectors/
│   └── {coord_key}/                  <-- ข้อมูลสถานะของแต่ละ Sector ("0,0", "3,3", ฯลฯ)
│       ├── challengers/
│       │   └── {character_name}/
│       │       ├── character_name: string
│       │       ├── meseta: integer (ยอดสะสมทุกช่องใน Sector นี้)
│       │       ├── client_version: string
│       │       ├── security_status: string
│       │       ├── status: string ("claimed" | "contributing" | "BLOCKED_INSECURE_VERSION")
│       │       ├── slot: integer (ช่องปัจจุบันที่ประจำการ)
│       │       ├── farming_rate_mhr: integer
│       │       ├── farmingRateMhr: integer
│       │       ├── meseta_per_hour: integer
│       │       └── lastUpdated: timestamp (ms)
│       ├── sub_cells/
│       │   └── {slot}/               <-- แต่ละช่องย่อย 1-4 (Quadrant Sub-cells)
│       │       └── challengers/
│       │           └── {character_name}/
│       │               ├── character_name: string
│       │               ├── meseta: integer (ยอดเงินสะสมในช่องย่อยนี้)
│       │               ├── client_version: string
│       │               ├── security_status: string
│       │               ├── slot: integer
│       │               ├── farming_rate_mhr: integer
│       │               ├── farmingRateMhr: integer
│       │               ├── meseta_per_hour: integer
│       │               └── lastUpdated: timestamp (ms)
│       └── total_meseta: integer
├── latest_telemetry/                 <-- สัญญาณ Telemetry ล่าสุดสำหรับ Realtime Pulse
│   ├── character_name: string
│   ├── meseta: integer
│   ├── coord_key: string
│   ├── slot: integer
│   └── timestamp: timestamp (ms)
└── activity_feed/ & war_logs/
    └── {auto_id}/                    <-- บันทึกกิจกรรมสด (Event Log)
        ├── character_name: string
        ├── action / type: string ("MESETA" | "SECURITY_WARNING")
        ├── meseta: integer
        ├── gain: integer
        ├── client_version: string
        ├── security_status: string
        ├── coord: string
        └── timestamp: timestamp (ms)
```

---

## 3. รายละเอียด Payload Schema

### 3.1 Operative Profile Schema
* **URL:** `PUT/PATCH /arks_war_room/operatives/{character_name}.json`
* **ตัวอย่าง JSON Payload:**
```json
{
  "character_name": "Vale3neko",
  "meseta": 25000000,
  "raw_meseta": 25000000,
  "client_version": "7.1.0",
  "version": "7.1.0",
  "security_status": "SECURE",
  "version_security_valid": true,
  "sector_coord": {
    "x": 0,
    "y": 0,
    "slot": 1
  },
  "coord_key": "0,0",
  "slot": 1,
  "lastUpdated": 1726831200000
}
```

> ⚠️ **กฎความปลอดภัยเวอร์ชัน (Version Security Gate):**
> หากตรวจพบไคลเอนต์เวอร์ชันที่มีช่องโหว่ เช่น `7.0.0-alpha` (ซึ่งถูกแก้บั๊กเป็น `7.1.0` แล้ว) หรือเวอร์ชันที่ถูกเพิกถอน (Revoked):
> - ฟิลด์ `meseta` จะถูกปรับเป็น `0` ทันที (ไม่นับเงินเข้าฐานข้อมูล)
> - ฟิลด์ `security_status` จะแสดงเป็น `"REVOKED_VERSION_INSECURE"`
> - ฟิลด์ `version_security_valid` จะเป็น `false`
> - ใน Sector และ Sub-cell Challengers ค่าเงินสะสมจะไม่ถูกเพิ่ม และสถานะจะถูกปรับเป็น `"BLOCKED_INSECURE_VERSION"`

### 3.2 Sector Sub-Cell & Challenger Schema
* **Sub-Cell Challenger URL:** `PUT /arks_war_room/sectors/{coord_key}/sub_cells/{slot}/challengers/{character_name}.json`
* **Sector Challenger URL:** `PUT /arks_war_room/sectors/{coord_key}/challengers/{character_name}.json`
* **Multi-Path Atomic Optimization:** ซิงค์ผ่าน `PATCH /arks_war_room.json` รวบทุกเส้นทางเป็น 1 Request:
```json
{
  "operatives/Vale3neko": {
    "character_name": "Vale3neko",
    "meseta": 25000000,
    "raw_meseta": 25000000,
    "slot_meseta": 10000000,
    "sector_meseta": 25000000,
    "client_version": "7.1.0",
    "security_status": "SECURE",
    "version_security_valid": true,
    "farming_rate_mhr": 3500000,
    "farmingRateMhr": 3500000,
    "meseta_per_hour": 3500000,
    "coord_key": "0,0",
    "slot": 1,
    "lastUpdated": 1726831200000
  },
  "sectors/0,0/sub_cells/1/challengers/Vale3neko": {
    "character_name": "Vale3neko",
    "meseta": 10000000,
    "slot": 1,
    "client_version": "7.1.0",
    "security_status": "SECURE",
    "farming_rate_mhr": 3500000,
    "farmingRateMhr": 3500000,
    "meseta_per_hour": 3500000,
    "lastUpdated": 1726831200000
  },
  "sectors/0,0/challengers/Vale3neko": {
    "character_name": "Vale3neko",
    "meseta": 25000000,
    "slot": 1,
    "status": "claimed",
    "client_version": "7.1.0",
    "security_status": "SECURE",
    "farming_rate_mhr": 3500000,
    "farmingRateMhr": 3500000,
    "meseta_per_hour": 3500000,
    "lastUpdated": 1726831200000
  },
  "latest_telemetry": {
    "character_name": "Vale3neko",
    "meseta": 25000000,
    "coord_key": "0,0",
    "slot": 1,
    "timestamp": 1726831200000
  }
}
```

### 3.3 Activity Feed Item Schema
* **URL:** `POST /arks_war_room/activity_feed.json`
* **ตัวอย่าง JSON Payload:**
```json
{
  "character_name": "Vale3neko",
  "action": "meseta_earned",
  "amount": 250000,
  "coord": "0, 0, 1",
  "timestamp": 1726831200000
}
```

---

## 4. พารามิเตอร์การหน่วงเวลาและ Heartbeat (Timing & Rate Limiting)

* **Debounce Window (`sync_debounce = 0.35` s):** ป้องกันการยิง Request ถี่เกินไปเมื่อมีการดรอปเงินต่อเนื่อง โดยจะรวบยอดคำขอไว้ส่งครั้งเดียวหลังไม่มีการเปลี่ยนแปลงเกิน 350 มิลลิวินาที
* **Heartbeat Interval (`heartbeat_interval = 5.0` s):** หากกำลังอยู่ในช่วงฟาร์มต่อเนื่อง จะส่งสัญญาณ Pulse ยืนยันสถานะออนไลน์ทุกๆ 5 วินาที
* **Offline Fallback:** หากส่งไม่สำเร็จหรือไม่มีการเชื่อมต่ออินเทอร์เน็ต ระบบจะไม่ทำให้แอปพลิเคชันค้าง (Non-blocking) และจะจัดเก็บลงแคช `%APPDATA%\NekoTrackerOffline\war_stats.json` ทันที
