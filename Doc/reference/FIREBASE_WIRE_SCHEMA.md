# 📡 NEKO Item & Meseta Tracker — Firebase RTDB Wire Schema (โครงสร้างข้อมูล Firebase)

> **สถานะ:** `[REFERENCE]` 🔵 — สเปคข้อตกลงการแลกเปลี่ยนข้อมูลผ่านเครือข่าย (Network Wire Contract)  
> **ฐานข้อมูล:** Google Firebase Realtime Database (RTDB)  
> **URL เริ่มต้น:** `https://arks-war-room-default-rtdb.asia-southeast1.firebasedatabase.app`  
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
├── operatives/
│   └── {character_name}/             <-- สถานะและสถิติตัวละครรายบุคคล
│       ├── character_name: string
│       ├── meseta: integer
│       ├── sector_coord: object {x, y, slot}
│       ├── coord_key: string ("X,Y")
│       ├── slot: integer (1..4)
│       └── lastUpdated: timestamp (ms)
├── sectors/
│   └── {coord_key}/                  <-- ข้อมูลสถานะของแต่ละ Sector ("0,0", "3,3", ฯลฯ)
│       ├── slots/
│       │   └── {slot}/               <-- ข้อมูลช่องย่อย (1..4)
│       │       ├── character_name: string
│       │       ├── meseta: integer
│       │       ├── status: string ("claimed" | "contributing")
│       │       ├── target: integer (25000000)
│       │       ├── progress: float (0.0 .. 100.0)
│       │       └── lastUpdated: timestamp (ms)
│       └── total_meseta: integer
└── activity_feed/
    └── {auto_id}/                    <-- บันทึกกิจกรรมสด (Event Log)
        ├── character_name: string
        ├── action: string
        ├── amount: integer
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

### 3.2 Sector Sub-Cell (Slot) Schema
* **URL:** `PUT/PATCH /arks_war_room/sectors/{coord_key}/slots/{slot}.json`
* **ตัวอย่าง JSON Payload:**
```json
{
  "character_name": "Vale3neko",
  "meseta": 25000000,
  "status": "claimed",
  "target": 25000000,
  "progress": 100.0,
  "lastUpdated": 1726831200000
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
