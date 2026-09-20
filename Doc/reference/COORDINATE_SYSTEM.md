# 🗺️ NEKO Item & Meseta Tracker — Coordinate System Specification (ระบบพิกัดสงคราม)

> **สถานะ:** `[REFERENCE]` 🔵 — ข้อกำหนดทางเทคนิคระบบพิกัดอวกาศ (Coordinate System Reference)  
> **ขอบเขต:** อธิบายโครงสร้างกริด Sector, การแบ่ง 4 ช่องย่อย (Quadrant Slots), เป้าหมายเงิน Meseta, และอัลกอริทึมการแปลงพิกัด  

---

## 1. ขอบเขตกริตกาแล็กซี (ARKS Galaxy Grid System)

แผนที่สงคราม ARKS War Room แบ่งพื้นที่อวกาศออกเป็นตาราง **Sector** สองมิติ (แกน X และ Y) พร้อมช่วงขอบเขตที่รองรับดังนี้:

| มิติ / แกน | ค่าต่ำสุด (MIN) | ค่าสูงสุด (MAX) | จำนวน Sector ทั้งหมด |
| :--- | :---: | :---: | :---: |
| **แกน X (Sector X)** | `-12` | `+25` | 38 ช่อง |
| **แกน Y (Sector Y)** | `-11` | `+9` | 21 ช่อง |
| **รวมทั้งกาแล็กซี** | — | — | **798 Sectors** |

---

## 2. ระบบ 4 ช่องย่อยต่อ Sector (Quadrant Sub-Cell Slots)

เพื่อให้ผู้เล่นและทีมสามารถแบ่งพื้นที่กันยึดครองในแต่ละ Sector ได้อย่างละเอียดยิ่งขึ้น แต่ละ Sector จึงถูกแบ่งออกเป็น **4 ช่องย่อย (Slots 1 - 4)** ตามระบบจตุภาค (Quadrants):

```
+------------------------------------+------------------------------------+
|                                    |                                    |
|              SLOT #1               |              SLOT #2               |
|          NW (North-West)           |          NE (North-East)           |
|             "บนซ้าย"               |             "บนขวา"                |
|                                    |                                    |
|   🎯 เป้าหมาย: 25,000,000 N-Meseta |   🎯 เป้าหมาย: 25,000,000 N-Meseta |
+------------------------------------+------------------------------------+
|                                    |                                    |
|              SLOT #3               |              SLOT #4               |
|          SW (South-West)           |          SE (South-East)           |
|            "ล่างซ้าย"              |            "ล่างขวา"               |
|                                    |                                    |
|   🎯 เป้าหมาย: 25,000,000 N-Meseta |   🎯 เป้าหมาย: 25,000,000 N-Meseta |
+------------------------------------+------------------------------------+
```

### สรุปข้อมูลช่องย่อยและเป้าหมายเงิน
* **เป้าหมายต่อช่องย่อย (SLOT_TARGET_MESETA):** `25,000,000` N-Meseta (25M)
* **เป้าหมายรวมทั้ง Sector (SECTOR_TARGET_MESETA):** `100,000,000` N-Meseta (100M)
* **การคำนวณเปอร์เซ็นต์ความคืบหน้า:**
  $$\text{Progress \%} = \min\left(100.0, \frac{\text{Current Meseta}}{25,000,000} \times 100\right)$$

---

## 3. พิกัดจุดสังเกตสำคัญในจักรวาล ARKS (Landmark Coordinates)

ระบบมีการฝังพิกัดของสถานที่สำคัญตามเนื้อเรื่อง PSO2 และ NGS ไว้ในตัวแปร `LANDMARK_COORDINATES`:

| Landmark Key | ชื่อสถานที่ (Location Name) | Sector X | Sector Y | คำอธิบาย |
| :--- | :--- | :---: | :---: | :--- |
| `oracle_fleet` | Galactic Core / Oracle Fleet | `0` | `0` | ศูนย์กลางจักรวาลและกองยาน Oracle |
| `central_city` | Halpha / Central City (PSO2:NGS) | `3` | `3` | เมืองศูนย์กลางของดาว Halpha |
| `earth` | Solar System (โลก / Earth) | `9` | `-3` | ดาวเคราะห์โลก |
| `sun` | Solar System (ดวงอาทิตย์ / Sun) | `8` | `-3` | จุดศูนย์กลางระบบสุริยะ |
| `mars` | Mars (ดาวอังคาร) | `9` | `-4` | ดาวอังคาร |
| `naberius` | Naberius (PSO2: Base) | `-2` | `-2` | ดาวนาเบเรียสจากเนื้อเรื่อง PSO2 ภาคแรก |
| `amduskia` | Amduskia | `-3` | `-3` | ดาวมังกรอัมดุสเกีย |
| `lillipa` | Lillipa | `-1` | `-3` | ดาวทะเลทรายลิลลิปา |
| `project_hail_mary` | Project Hail Mary Outpost | `20` | `7` | ฐานสำรวจอวกาศลึก |

---

## 4. โครงสร้างคลาส `TargetCoord`

คลาส `TargetCoord` (`modules/war_mode/war_service.py`) สืบทอดคุณสมบัติมาจาก `tuple`:
* **โครงสร้างภายใน:** `(sector_x, sector_y, slot)`
* **การจำกัดขอบเขตอัตโนมัติ (Clamping):**
  - บังคับ `x` ให้อยู่ระหว่าง `SECTOR_X_MIN` (-12) ถึง `SECTOR_X_MAX` (25)
  - บังคับ `y` ให้อยู่ระหว่าง `SECTOR_Y_MIN` (-11) ถึง `SECTOR_Y_MAX` (9)
  - บังคับ `slot` ให้อยู่ระหว่าง `SLOT_MIN` (1) ถึง `SLOT_MAX` (4)
* **Properties ที่พร้อมใช้งาน:**
  - `coord.x` หรือ `coord.sector_x`: ค่าพิกัดแกน X (int)
  - `coord.y` หรือ `coord.sector_y`: ค่าพิกัดแกน Y (int)
  - `coord.slot`: หมายเลขช่องย่อย 1-4 (int)
  - `coord.slot_name`: รหัสย่อ Quadrant (`"NW"`, `"NE"`, `"SW"`, `"SE"`)
  - `coord.slot_label`: ป้ายชื่อภาษาไทย (`"#1 NW (บนซ้าย)"`)
  - `coord.coord_key`: คีย์ระบุ Sector สำหรับ Firebase (`"0,0"`)
* **Backward Compatibility:** รองรับการเปรียบเทียบความเท่ากัน `==` กับทั้ง 3-tuple `(x, y, slot)` และ 2-tuple `(x, y)`

---

## 5. รูปแบบการแปลงพิกัด (Smart Coordinate Parsing)

ฟังก์ชัน `WarService.parse_coordinate(input_str)` รองรับการป้อนข้อมูลได้ถึง 7 รูปแบบ:

| ลำดับ | ชนิดข้อมูล / รูปแบบ | ตัวอย่างข้อมูลนำเข้า (Input) | ผลลัพธ์ที่ได้ (`TargetCoord`) |
| :---: | :--- | :--- | :--- |
| **1** | ตัวเลข 3 จำนวนคั่นด้วยคอมมา | `"0, 0, 1"` หรือ `"3, 3, 4"` | `TargetCoord(0, 0, 1)`, `TargetCoord(3, 3, 4)` |
| **2** | รูปแบบเครื่องหมายชาร์ป (Hash) | `"0,0#1"` หรือ `"3, 3 # 4"` | `TargetCoord(0, 0, 1)`, `TargetCoord(3, 3, 4)` |
| **3** | รูปแบบวงเล็บก้ามปู (Bracket) | `"[0, 0, 1]"` หรือ `"[3, 3, 4]"` | `TargetCoord(0, 0, 1)`, `TargetCoord(3, 3, 4)` |
| **4** | JSON Object หรือ JSON String | `{"x": 0, "y": 0, "slot": 1}`<br>`{"sector_x": 3, "sector_y": 3, "slot": 4}` | `TargetCoord(0, 0, 1)`, `TargetCoord(3, 3, 4)` |
| **5** | ข้อความที่คัดลอกมาจาก Web UI | `"คัดลอกพิกัด [8, -2] ช่อง #3 ไปใส่ในโปรแกรม"`<br>`"Sector [0, 0] · ช่อง #2"` | `TargetCoord(8, -2, 3)`, `TargetCoord(0, 0, 2)` |
| **6** | รูปแบบชื่อทิศทาง Quadrant | `"0, 0 NW"` หรือ `"0, 0 บนซ้าย"`<br>`"3, 3 SE"` หรือ `"3, 3 ล่างขวา"` | `TargetCoord(0, 0, 1)`, `TargetCoord(3, 3, 4)` |
| **7** | Fallback 2 จำนวน (ระบุช่องเป็น 1) | `"0, 0"` หรือ `"[15, -8]"` หรือ `"X: 12, Y: -5"` | `TargetCoord(0, 0, 1)`, `TargetCoord(15, -8, 1)` |
