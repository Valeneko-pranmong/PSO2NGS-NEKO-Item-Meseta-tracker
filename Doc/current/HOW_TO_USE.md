# 🌸 NEKO Item & Meseta Tracker — คู่มือการใช้งาน (User Guide / 使い方ガイド)

> **Official Community & Credits:**  
> **NEKO★FAMILY PSO2:NGS Community discord.gg/fkjXW9AJ6a**  
> 🔗 **Discord Link:** [https://discord.gg/fkjXW9AJ6a](https://discord.gg/fkjXW9AJ6a)  
> 🌐 **Web ARKS War Room:** [https://arks-war-room.vercel.app/](https://arks-war-room.vercel.app/)

---

## 📑 สารบัญภาษา / Language Index / 目次
* [🇹🇭 1. ภาษาไทย (Thai Guide)](#1-ภาษาไทย-thai-guide)
* [🇬🇧 2. English Guide](#2-english-guide)
* [🇯🇵 3. 日本語 (Japanese Guide)](#3-日本語-japanese-guide)

---

## 1. 🇹🇭 ภาษาไทย (Thai Guide)

ยินดีต้อนรับสู่ **NEKO Item & Meseta Tracker (PSO2:NGS)** เครื่องมือช่วยเล่นสำหรับติดตามรายได้ N-Meseta, อัตราความเร็วต่อชั่วโมง (M/hr), ไอเท็มดรอป, และแผนที่สงคราม ARKS War Room แบบ Real-time!

### 1.1 การเริ่มต้นใช้งาน & การเลือกโฟลเดอร์ Log
1. **โฟลเดอร์ Log ของเกม:** ตัวเกม Phantasy Star Online 2: New Genesis จะบันทึกไฟล์เหตุการณ์ `ActionLogYYYYMMDD_0.txt` อัตโนมัติในเครื่องของคุณที่ตำแหน่ง:
   ```text
   Documents\SEGA\PHANTASYSTARONLINE2\log_ngs
   ```
2. **การตั้งค่าในโปรแกรม:**
   - คลิกปุ่ม **"📂 เลือกโฟลเดอร์ Log"** ที่แถบเมนูด้านซ้าย
   - เลือกโฟลเดอร์ `log_ngs` แล้วกดยืนยัน
   - โปรแกรมจะตรวจจับไฟล์ Log สดทันที (หรือค้นหาโฟลเดอร์ Log ของเกมให้โดยอัตโนมัติ)
3. **ระบบ Zero-Login (ไม่ต้องล็อกอิน):**
   - โปรแกรมจะตรวจจับชื่อตัวละครในเกม (Character Name) และรหัสผู้เล่น (Player ID) จากไฟล์ Log โดยอัตโนมัติ
   - ไม่มีการขอ ไม่มีการจัดเก็บ และไม่มีการส่งรหัสผ่านใดๆ ทั้งสิ้น ปลอดภัย 100%
4. **ความปลอดภัย 100% TOS Safe:**
   - มอนิเตอร์เฉพาะไฟล์ข้อความ ActionLog ภายนอกเท่านั้น
   - ไม่มีการแตะต้อง Memory ของเกม ไม่มีการ Hook API หรือฉีด DLL ใดๆ จึงปลอดภัยจากการแบน (Ban-free) 100%
5. **การันตีความเป็นส่วนตัวในโหมดออฟไลน์ (Offline Privacy Guarantee):**
   - เมื่อใช้งานในโหมด Offline หน้าหลัก โปรแกรมจะไม่ส่งคำขอหรือข้อมูลใดๆ ออกสู่อินเทอร์เน็ตเด็ดขาด (Zero Telemetry Leakage)
   - การซิงค์ข้อมูลกับคลาวด์จะเริ่มต้นเฉพาะเมื่อคุณคลิกปุ่ม **"⚔️ เข้าร่วมสงคราม (ARKS War)"** เท่านั้น

### 1.2 การติดตามเงิน Meseta & รายการของดรอป
* **ยอดเงินรอบนี้ (Session):** คำนวณยอดเงิน N-Meseta สุทธิที่ได้รับในรอบฟาร์มนี้
* **เงินที่มีในกระเป๋า (Wallet):** แสดงยอดเงินคงเหลือปัจจุบันในตัวละคร
* **ความเร็ว (M/hr):** คำนวณอัตราความเร็วเงินต่อชั่วโมงแบบ Real-time
* **First-Drop Inception:** ระบบจะเริ่มจับเวลาเมื่อเงินหรือไอเท็มชิ้นแรกดรอปจริง เพื่อไม่ให้เวลาว่างขณะยืนในล็อบบี้มาดึงอัตรา M/hr ของคุณให้ต่ำลง
* **Item Drops List:** ค้นหาและดูจำนวนไอเท็ม อุปกรณ์ และแคปซูลที่ดรอป
* **Watch List Filter:**
  - คลิกปุ่ม **"แก้ไข Watch List"** เพื่อระบุชื่อไอเท็มที่ต้องการโฟกัส (บรรทัดละ 1 ชื่อ) แล้วกดบันทึก
  - เปิดสวิตช์ **"กรองเฉพาะ Watch List"** เพื่อกรองแสดงเฉพาะไอเท็มหายากที่คุณสนใจ
* **รีเซ็ตข้อมูล (Reset):** คลิกปุ่ม **"รีเซ็ตข้อมูล (Reset)"** เพื่อล้างยอดเงิน เวลา และไอเท็มดรอปเพื่อเริ่มรอบฟาร์มใหม่

### 1.3 โหมด Gadget Overlay (หน้าต่างลอยทับหน้าจอเกม)
* **Full Overlay (Item & Meseta):** แสดงยอดเงิน Meseta รวม, เงินในกระเป๋า, อัตรา M/hr, เวลาที่ฟาร์ม, และ 4 ไอเท็มดรอปล่าสุด
* **Mini Overlay (Meseta Only):** ขนาดเล็กกะทัดรัดพิเศษ โปร่งใส แสดงเฉพาะตัวเลขเงิน Meseta และกระเป๋า เหมาะสำหรับเปิดขณะต่อสู้อย่างจริงจัง
* **การเลื่อนตำแหน่ง (Draggable):** คลิกเมาส์ซ้ายค้างที่แถบด้านบนของ Overlay เพื่อลากย้ายตำแหน่งไปยังจุดที่ต้องการบนหน้าจอได้อย่างอิสระ

### 1.4 โหมดสงครามออนไลน์ ARKS War Room (Coordinate War Engine V9)
* **ปรัชญาและกฎกติกาหลัก:** **"เกมแค่เติมเงินเข้าไปในช่อง ใครใส่เยอะคนนั้นเป็นเจ้าของ"** (V9 Release)
* **การเข้าร่วมสงคราม:** คลิกปุ่ม **"⚔️ เข้าร่วมสงคราม (ARKS War)"** ที่แถบเมนู
* **พิกัด Sector & 4 Quadrant Slots:**
  - แกน Sector X: `[-12..25]`, แกน Sector Y: `[-11..9]` รวม 798 Sectors ทั่วกาแล็กซี
  - แต่ละ Sector แบ่งออกเป็น 4 ช่องย่อย: `#1` (NW - บนซ้าย), `#2` (NE - บนขวา), `#3` (SW - ล่างซ้าย), `#4` (SE - ล่างขวา) ขนาดช่องละ $300\text{px} \times 300\text{px}$
  - **มูลค่าตั้งต้นก่อนยึด 10M:** แต่ละช่องย่อยมีเกณฑ์ปลดล็อกยึดครองที่ **10,000,000 N-Meseta (10M ℳ)**
  - **การแย่งชิงสิทธิ์ (Clash & Hostile Overwrite):** ใครที่เติมเงินฟาร์มใส่ช่องนั้นเกิน 10M และมียอดเงินสูงสุด จะได้เป็นเจ้าของช่องนั้นทันที (`👑 Name`) หากมีผู้เล่นอื่นมาเติมเงินแซง สิทธิ์ความเป็นเจ้าของจะถูกแย่งชิงไปทันที!
  - **การปลดแอกสมบูรณ์ (100% Liberated):** เซกเตอร์จะเปลี่ยนสถานะเป็นยึดครองสมบูรณ์เมื่อยึดครองครบทั้ง 4 ช่องย่อย (ยอดรวม $\ge 40\text{M ℳ}$)
  - **การหลอมรวมผืนแผ่นดิน (Seamless Continent):** หากทั้ง 4 ช่องย่อยถูกยึดครองโดยผู้เล่นคนเดียวกัน เส้นแบ่งภายในจะหายไปและหลอมรวมเป็นผืนดินเรืองแสงผืนเดียว
* **ระบบวางพิกัดอัจฉริยะ (Smart Paste):**
  - คัดลอกพิกัดจากหน้าเว็บสงครามแล้วกดปุ่ม **"📋 วาง"** (รองรับรูปแบบ `15, -6, 2` หรือ `(15, -6, 2)`)
  - หรือเลือกพิกัดสำคัญจากเมนู Landmark: Core [0, 0], NGS [3, 3], Earth [9, -3], Sun [8, -3]
  - **สถานะพร้อมรบ (Standby Presence):** เมื่อเชื่อมต่อ Tracker แล้ว แม้จะมียอดเงินสะสม $0\text{ ℳ}$ ตัวละครจะปรากฏตัวในทำเนียบนักรบพร้อมป้ายพิกัด `📍 [+X, -Y] #Slot` ยืนยันว่าออนไลน์พร้อมรบสด
* **การฟาร์มต่อเนื่องหลายช่องย่อย (Multi-Slot Continuous Farming):**
  - คุณสามารถสลับพิกัดหรือเปลี่ยนช่องย่อยไปช่วยเพื่อนในจุดต่างๆ ได้อย่างอิสระ
  - ยอดเงินที่คุณเคยฟาร์มไว้ในช่องก่อนหน้าจะยังคงอยู่และถูกนับรวมสะสมต่อเนื่อง ไม่มีการถูกล้างหรือหายไป
* **ระบบซิงค์สดออนไลน์ (Cloud Realtime Sync):** ส่งยอดเงินที่ฟาร์มได้และพิกัดเป้าหมายขึ้นระบบสงครามออนไลน์แบบเรียลไทม์ โดยระบบจะรวบรวมและส่งข้อมูลให้อัตโนมัติอย่างรวดเร็วและประหยัดอินเทอร์เน็ต
* **เว็บแผนที่สงครามสด (Tactical Web Observability):**
  - คลิกปุ่ม **"🪐 ARKS War Room (Web)"** เพื่อเปิดดูแผนที่สดระดับกาแล็กซีที่ `https://arks-war-room.vercel.app/`
  - มีระบบ **Tactical Spotlight** ส่องสว่างทั่วทั้งดาราจักรเมื่อคลิกชื่อผู้เล่นในทำเนียบนักรบ, **Reactive Target Inspector** อัปเดตสด 60fps, และ **Top 10 Cyber Neon Signature Colors**

### 1.5 ชุมชน & เครดิตอย่างเป็นทางการ
* **คอมมูนิตี้ Discord ทางการ:**  
  **NEKO★FAMILY PSO2:NGS Community discord.gg/fkjXW9AJ6a**  
  [https://discord.gg/fkjXW9AJ6a](https://discord.gg/fkjXW9AJ6a)
* พูดคุย แลกเปลี่ยนเทคนิคการฟาร์ม แจ้งปัญหา แนะนำฟีเจอร์ใหม่ และร่วมทำสงคราม ARKS War Room

---

## 2. 🇬🇧 English Guide

Welcome to **NEKO Item & Meseta Tracker (PSO2:NGS)**, a high-performance companion utility designed for real-time N-Meseta tracking, hourly velocity (M/hr), rare drop monitoring, and collaborative galaxy conquest in the **ARKS War Room**!

### 2.1 Getting Started & Log Directory Setup
1. **Locating PSO2:NGS Game Logs:** The game client automatically outputs gameplay and drop records to `ActionLogYYYYMMDD_0.txt` in your local documents folder:
   ```text
   Documents\SEGA\PHANTASYSTARONLINE2\log_ngs
   ```
2. **Configuring in the Tracker:**
   - Click the **"📂 Select Log Folder"** button in the left sidebar.
   - Browse to your `log_ngs` directory and confirm.
   - The application immediately detects and reads the newest active log stream.
3. **Zero-Login Architecture:**
   - Discovers your active in-game character name and player ID directly from log events.
   - Never requests, stores, or transmits SEGA ID passwords, tokens, or emails.
4. **100% TOS Safe & Non-Invasive:**
   - Passively monitors local text log files on disk.
   - Does NOT inspect process memory (`OpenProcess` / `ReadProcessMemory`), does NOT hook DirectX APIs, and uses zero DLL injections. Fully compliant and safe from anti-cheat bans.

### 2.2 Tracking Meseta Earnings & Drops
* **Session Earnings:** Net N-Meseta accumulated across pickup actions, auto-sells, and rewards.
* **Current Wallet:** Active character wallet balance in real-time.
* **Farming Speed (M/hr):** Dynamic hourly velocity calculated from active farming duration.
* **First-Drop Inception:** The timer begins only when your first drop or Meseta pickup occurs, preventing lobby idle time from deflating your M/hr metrics.
* **Dropped Items List:** Filter and inspect all dropped equipment, capsules, and materials.
* **Watch List Filter:**
  - Click **"Edit Watch List"** to specify items you want to focus on (1 per line).
  - Toggle the **"Enable Watch List Filter"** switch to view only desired items and filter out junk drops.
* **Reset Session:** Click **"Reset (Start Over)"** at any time to clear metrics and begin a fresh run.

### 2.3 Gadget Mode (Floating Game Overlay)
* **Full Overlay (Item & Meseta):** Floating, semi-transparent HUD displaying total session N-Meseta, current wallet, farming duration, M/hr rate, and recent 4 item drops.
* **Mini Overlay (Meseta Only):** Ultra-compact floating counter showing only your live session earnings and wallet balance, keeping your battle screen clean.
* **Draggable Positioning:** Click and drag the top banner of the overlay to reposition it anywhere across single or multi-monitor configurations.

### 2.4 ARKS War Room Mode (Coordinate War Engine V9)
* **Core Philosophy & Rule:** **"A pure slot-conquest game: players deposit Meseta into coordinate slots; whoever puts in the highest amount exceeding 10M becomes the owner."** (V9 Release)
* **Entering War Mode:** Click **"⚔️ Enter War (ARKS War)"** in the left sidebar.
* **Sector Coordinates & 4 Quadrant Slots:**
  - Sector X: `[-12..25]`, Sector Y: `[-11..9]` spanning 798 sectors.
  - 4 Quadrant Sub-cell slots per sector: `#1` (NW), `#2` (NE), `#3` (SW), `#4` (SE), each $300\text{px} \times 300\text{px}$.
  - **Base Capture Threshold: 10,000,000 N-Meseta (10M ℳ)** per slot.
  - **Clash & Hostile Overwrite:** Whoever deposits more Meseta than the current leader immediately seizes slot ownership (`👑 Name`).
  - **100% Macro Sector Liberation:** A sector is fully liberated once all 4 slots are unlocked ($\ge 40\text{M ℳ}$ total).
  - **Seamless Continent:** When all 4 slots belong to the same operative, internal dividing lines disappear into a unified glowing territory.
* **Smart Coordinate Parser & Paste:**
  - Copy coordinates from the web map and click **"📋 Paste"** (supports `15, -6, 2`, `(15, -6, 2)`, etc.).
  - Select canonical landmarks: Core [0, 0], NGS [3, 3], Earth [9, -3], Sun [8, -3], etc.
  - **Standby Presence Visibility:** Operatives connected to Neko Tracker appear in the web roster ready for battle even at 0 ℳ (`📍 [+X, -Y] #Slot`).
* **Cloud Realtime Telemetry Sync:** Automatically streams your earned contributions and active coordinates live to the online War Room network with low-latency background synchronization.
* **Live Galaxy Tactical Map (Web Observability):**
  - Click **"🪐 ARKS War Room (Web)"** to view the full interactive map at `https://arks-war-room.vercel.app/`.
  - Features Interactive Tactical Spotlight (click operative to bloom all their holdings), Reactive Target Inspector, and Top 10 Major Powers Cyber Neon palette.

### 2.5 Community & Official Credits
* **Official Discord Community:**  
  **NEKO★FAMILY PSO2:NGS Community discord.gg/fkjXW9AJ6a**  
  [https://discord.gg/fkjXW9AJ6a](https://discord.gg/fkjXW9AJ6a)
* Join us to team up for PSE Burst farming, trigger runs, bug reports, and ARKS War Room operations!

---

## 3. 🇯🇵 日本語 (Japanese Guide)

**NEKO アイテム＆メセタトラッカー (PSO2:NGS)** へようこそ！  
リアルタイムN-メセタ集計、時給計算 (M/hr)、ドロップアイテム監視、そして銀河戦況共有モード **ARKS War Room** を備えた高機能コンパニオンツールです。

### 3.1 初期設定とログフォルダの指定
1. **ゲームログの保存場所:** PSO2:NGS クライアントは、プレイ中の獲得記録を以下のローカルフォルダへ自動出力します:
   ```text
   Documents\SEGA\PHANTASYSTARONLINE2\log_ngs
   ```
2. **トラッカーでの指定手順:**
   - 左側サイドバーの **「📂 ログフォルダを選択」** ボタンをクリックします。
   - 上記の `log_ngs` フォルダを選択して確定します。
   - アプリケーションが自動的に最新のActionLogファイルを検知し、監視を開始します。
3. **Zero-Login（アカウント不要）設計:**
   - ログからキャラクター名とプレイヤーIDを自動判別します。
   - SEGA IDやパスワードの入力・保存・送信は一切不要です。
4. **100% 規約遵守・安全設計 (TOS Safe):**
   - ローカルのテキストログを受動的に読み取るのみの設計です。
   - ゲームプロセスメモリの読み書き (`OpenProcess` / `ReadProcessMemory`) やDirectXフック、DLLインジェクションは一切行いません。BANリスクゼロで安心してご利用いただけます。

### 3.2 メセタ獲得量＆アイテムドロップの追跡
* **今回の獲得メセタ (Session):** ドロップ拾得、自動売却、クエスト報酬から獲得した純N-メセタ額をリアルタイム集計。
* **現在の所持メセタ (Wallet):** ゲーム内の最新所持メセタ残高を表示。
* **獲得時給 (M/hr):** 実稼働時間に基づき、1時間あたりの獲得速度を算出。
* **初回ドロップ時タイマースタート:** ロビーでの放置時間による時給低下を防ぐため、最初のドロップが発生した瞬間から計測を開始します。
* **ドロップアイテム一覧:** 獲得した装備、特殊能力カプセル、素材アイテムを個数・時間付きで記録。
* **ウォッチリストフィルター機能:**
  - **「ウォッチリスト編集」** ボタンから注目アイテム名を登録（1行に1つ）。
  - **「ウォッチリストフィルター有効」** スイッチをONにすると、指定したアイテムのみが表示されます。
* **セッションリセット:** **「リセット (Reset)」** ボタンでいつでも集計を初期化し、新しい周回を開始できます。

### 3.3 ガジェットモード (最前面ゲームオーバーレイ)
* **フルオーバーレイ (Item & Meseta):** 獲得メセタ、所持メセタ、周回時間、時給 (M/hr)、最新4件のドロップアイテムをゲーム画面の上に半透明で常時浮遊表示。
* **ミニオーバーレイ (Meseta Only):** 戦闘の邪魔にならない超小型設計。今回の獲得メセタと所持メセタのみをコンパクトに表示。
* **ドラッグ移動:** オーバーレイ上部のヘッダーバーを左クリックしたままドラッグすることで、画面上の好きな位置へ移動できます。

### 3.4 ARKS War Room モード (Coordinate War Engine V9 銀河セクター制圧作戦)
* **コアルールと基本理念:** **『スロットにメセタを預け入れ、10M超えで最も多く入れた者が占有者となる』** (V9 Release)
* **作戦室への参加:** 左側メニューの **「⚔️ 作戦参加 (ARKS War)」** をクリック。
* **セクター座標と4分割象限スロット:**
  - セクターX: `[-12..25]`、セクターY: `[-11..9]`（全798セクター展開）。
  - 各セクターは4つのスロットに分割: `#1` (NW), `#2` (NE), `#3` (SW), `#4` (SE) 各 $300\text{px} \times 300\text{px}$。
  - **占有閾値 10M:** 各スロットは **10,000,000 N-メセタ (10M ℳ)** の投入で占有権を獲得 (`👑 Name`)。
  - **占有権強奪 (Clash & Hostile Overwrite):** 他プレイヤーがそのスロットにさらに多くのメセタを投入した場合、即座に占有権が交代します！
  - **セクター完全解放 (100% Liberated):** 4スロットすべてが制圧された時点でセクター完全解放 ($\ge 40\text{M ℳ}$)。
  - **シームレス大陸化 (Seamless Continent):** 4スロットすべてを同一プレイヤーが制圧すると、内部境界線が消滅して1つの巨大ネオン領土に統合されます。
* **スマート座標貼り付け:**
  - Webマップからコピーした座標文字列を **「📋 貼付」** ボタンで一発入力（`15, -6, 2` や `(15, -6, 2)` に対応）。
  - 主要拠点プリセット（Core [0, 0], NGS [3, 3], 地球 [9, -3], 太陽 [8, -3] 等）からも選択可能。
  - **スタンバイ出撃可視化:** 0 ℳであってもTrackerを接続すると作戦名簿に `📍 [+X, -Y] #Slot` スタンバイ状態として即座に可視化されます。
* **クラウドリアルタイム同期:** 獲得貢献度と作戦座標をオンライン作戦サーバーへ自動同期（高速レスポンスかつ低負荷なバックグラウンド通信）。
* **Web戦況マップ連携 (Tactical Web Observability):**
  - **「🪐 ARKS War Room (Web)」** をクリックしてブラウザで銀河戦況リアルタイムマップ (`https://arks-war-room.vercel.app/`) を閲覧可能。
  - 戦術スポットライト（プレイヤー領土の全銀河強調ハイライト）、リアクティブ・インスペクター (60fps)、Top 10 サイバーネオンパレット搭載。

### 3.5 公式コミュニティ＆クレジット
* **公式Discordコミュニティ:**  
  **NEKO★FAMILY PSO2:NGS Community discord.gg/fkjXW9AJ6a**  
  [https://discord.gg/fkjXW9AJ6a](https://discord.gg/fkjXW9AJ6a)
* アークス仲間との交流、PSEバースト周回、不具合報告、最新アップデート情報の入手、作戦連携などにお気軽にご参加ください！
