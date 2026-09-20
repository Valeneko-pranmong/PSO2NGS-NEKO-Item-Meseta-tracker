"""
Interactive 3-Language User Guide (How-To-Use) Dialog for NEKO Item & Meseta Tracker.
Supports English (Primary), Thai, and Japanese with live in-flight language switching,
tabbed category navigation, Discord community integration, and official credit:
'NEKO★FAMILY PSO2:NGS Community discord.gg/fkjXW9AJ6a'
"""

from __future__ import annotations

import os
import webbrowser
from typing import Any, Dict, List, Optional
import tkinter as tk
import customtkinter as ctk
from PIL import Image

from config import (
    FONT_FAMILY,
    COLOR_PINK_HEADER,
    COLOR_PINK_ACCENT,
    COLOR_PINK_SOFT,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_SUB,
    COLOR_TEXT_VAL,
    COLOR_DISCORD,
    COLOR_WATCHLIST,
    UI_RADIUS,
    ICON_FILENAME,
    LOGO_FILENAME,
    DEFAULT_DISCORD_URL,
    DISCORD_INVITE_SHORT,
    DISCORD_COMMUNITY_NAME,
    DISCORD_CREDIT_FULL,
    DEFAULT_WAR_ROOM_URL,
)
from modules.i18n import i18n, t
from modules.event_bus import event_bus


# Structured 3-Language Guide Content Catalog
GUIDE_SECTIONS: Dict[str, Dict[str, Any]] = {
    "en": {
        "tabs": [
            ("setup", "🚀 Setup & Logs"),
            ("tracking", "💰 Meseta & Items"),
            ("overlay", "🪟 Gadget Overlay"),
            ("war", "⚔️ ARKS War"),
            ("community", "🌸 Community & Credit"),
        ],
        "setup": {
            "title": "Getting Started & Log Setup",
            "cards": [
                {
                    "title": "📂 1. Selecting the PSO2:NGS Log Folder",
                    "badge": "Required",
                    "badge_color": "#0284C7",
                    "desc": "PSO2:NGS automatically records in-game currency pickups and item drops into local ActionLog files.",
                    "bullets": [
                        "Default game log location on Windows:",
                        "Documents\\SEGA\\PHANTASYSTARONLINE2\\log_ngs",
                        "Click '📂 Select Log Folder' in the sidebar and choose your log_ngs folder.",
                        "Once selected, the tracker automatically monitors active log streams in real-time.",
                    ],
                    "path_box": "Documents\\SEGA\\PHANTASYSTARONLINE2\\log_ngs",
                    "action_type": "select_folder",
                    "action_text": "📂 Select Log Folder Now",
                },
                {
                    "title": "👤 2. Zero-Login Architecture",
                    "badge": "Zero UAC / No Passwords",
                    "badge_color": "#10B981",
                    "desc": "The tracker values your security and privacy above everything else.",
                    "bullets": [
                        "Zero-Login: Discovers your active character name and player ID automatically from log events.",
                        "No credentials needed: Never asks for, stores, or transmits SEGA ID passwords or emails.",
                        "Character switching: Automatically detects when you switch characters and updates stats seamlessly.",
                    ],
                },
                {
                    "title": "🛡️ 3. 100% TOS Safe & Non-Invasive",
                    "badge": "Anti-Cheat Safe",
                    "badge_color": "#8B5CF6",
                    "desc": "Strict compliance with game terms of service (TOS) to guarantee zero account ban risk.",
                    "bullets": [
                        "Passive file monitoring only: Reads plain text ActionLog files already saved to disk.",
                        "Zero memory tampering: Never opens process memory (OpenProcess / ReadProcessMemory).",
                        "Zero DLL injection: Does not hook game DirectX APIs or install keyboard hooks.",
                        "Multi-layer anti-tamper: Validates log stream continuity, timestamps, and drop limits.",
                    ],
                },
            ],
        },
        "tracking": {
            "title": "Meseta & Item Drop Tracking",
            "cards": [
                {
                    "title": "💎 1. Session Earnings & Farming Velocity (M/hr)",
                    "badge": "Real-time Metrics",
                    "badge_color": "#D81B60",
                    "desc": "Track your income during PSE Burst grinding and boss triggers.",
                    "bullets": [
                        "Session Earnings: Net N-Meseta gained from item pickups, auto-sell, and quest rewards.",
                        "Current Wallet: Real-time balance of your active character's in-game wallet.",
                        "Speed (M/hr): Dynamic hourly velocity calculated from active farming duration.",
                        "First-Drop Inception: The session timer starts only upon your first drop or Meseta pickup, ensuring lobby idle time won't penalize your M/hr stats.",
                    ],
                },
                {
                    "title": "📦 2. Item Drop List & Search",
                    "badge": "Inventory Intelligence",
                    "badge_color": "#0284C7",
                    "desc": "All dropped equipment, capsules, and materials are logged with quantities and timestamps.",
                    "bullets": [
                        "Search Bar: Instantly filter items by name (e.g. 'Astraea', 'Refiner', 'Dualble').",
                        "Clean grouping: Duplicate drops are aggregated with real-time drop count badges.",
                    ],
                },
                {
                    "title": "🎯 3. Watch List Filter",
                    "badge": "Rare Item Focus",
                    "badge_color": "#EC4899",
                    "desc": "Focus on high-value drops and eliminate common equipment noise.",
                    "bullets": [
                        "Click 'Edit Watch List' in the sidebar to enter item names to monitor (1 per line).",
                        "Toggle 'Enable Watch List Filter' switch: only watchlisted items will appear in the list and overlay.",
                    ],
                },
                {
                    "title": "🔄 4. Resetting Session",
                    "badge": "Fresh Start",
                    "badge_color": "#6B7280",
                    "desc": "Start a clean farming session whenever you change areas or join a new party.",
                    "bullets": [
                        "Click 'Reset (Start Over)' to clear session earnings, elapsed time, and drop lists.",
                        "Seeks the log pointer to EOF so past historical drops won't contaminate the new run.",
                    ],
                },
            ],
        },
        "overlay": {
            "title": "Gadget Mode (Floating Game Overlay)",
            "cards": [
                {
                    "title": "🖥️ 1. Full Overlay (Item & Meseta)",
                    "badge": "Comprehensive HUD",
                    "badge_color": "#FF69B4",
                    "desc": "A sleek, semi-transparent game HUD that stays on top while you fight.",
                    "bullets": [
                        "Displays total session N-Meseta, current wallet, farming time, and hourly rate (M/hr).",
                        "Shows the 4 most recent dropped items with quantity badges.",
                        "Always-on-top: Stays visible over borderless-windowed PSO2:NGS.",
                        "Click 'Item & Meseta' in the sidebar to toggle on/off.",
                    ],
                },
                {
                    "title": "⚡ 2. Mini Overlay (Meseta Only)",
                    "badge": "Compact Floating Widget",
                    "badge_color": "#F06292",
                    "desc": "Ultra-compact display designed for zero distraction during intense combat.",
                    "bullets": [
                        "Only shows your live session Meseta and current wallet in a slim, elegant bar.",
                        "Dynamic bounds auto-fit prevents text clipping across all Windows DPI scalings.",
                        "Click 'Meseta' in the sidebar to toggle on/off.",
                    ],
                },
                {
                    "title": "🖱️ 3. Window Dragging & Positioning",
                    "badge": "Custom Layout",
                    "badge_color": "#8B5CF6",
                    "desc": "Customize the overlay location to fit your personal in-game HUD layout.",
                    "bullets": [
                        "Click and drag anywhere on the top bar of the overlay window to move it.",
                        "Position persists across monitor resolutions and multi-screen setups.",
                    ],
                },
            ],
        },
        "war": {
            "title": "Online ARKS War Room Mode (Coordinate War Engine V9)",
            "cards": [
                {
                    "title": "⚔️ 1. Coordinate Slot Conquest ('Deposit & Own')",
                    "badge": "V9 Core Engine",
                    "badge_color": "#3B82F6",
                    "desc": "Core Rule: 'Deposit Meseta into discrete slots — whoever deposits the highest amount exceeding 10M owns the slot.'",
                    "bullets": [
                        "Click '⚔️ Enter War' in the sidebar to switch to the tactical ARKS War Room interface.",
                        "Galaxy grid covers 798 sectors: Sector X [-12..25], Sector Y [-11..9].",
                        "Each Sector is divided into 4 sub-cell slots (#1 NW, #2 NE, #3 SW, #4 SE).",
                        "Base Capture Threshold: 10,000,000 N-Meseta (10M ℳ) per slot.",
                        "Clash & Hostile Overwrite: Whoever farms more Meseta in a slot immediately seizes ownership from the previous leader!",
                        "Macro Sector Liberation: A sector is 100% liberated when all 4 slots are captured (40M ℳ total).",
                        "Seamless Continent: When all 4 slots belong to the same operative, internal boundaries vanish into a unified glowing territory.",
                    ],
                },
                {
                    "title": "📋 2. Smart Coordinate Parser & Landmark Presets",
                    "badge": "Instant Alignment",
                    "badge_color": "#10B981",
                    "desc": "Align your farming output with team targets using one-click coordinate pasting.",
                    "bullets": [
                        "Copy coordinates from the web map and click '📋 Paste' (supports '15, -6, 2', '[15, -6, 2]', etc.).",
                        "Quickly select canonical landmarks: Core [0, 0], NGS [3, 3], Earth [9, -3], Sun [8, -3], etc.",
                        "Click '💾 Save' to lock target coordinates for telemetry synchronization.",
                        "Standby Presence: Operatives connected to Neko Tracker appear in the web roster ready for battle even at 0 ℳ.",
                    ],
                },
                {
                    "title": "⚡ 3. Realtime Cloud Telemetry & Web War Room HUD",
                    "badge": "Real-time 60fps",
                    "badge_color": "#F59E0B",
                    "desc": "Real-time debounced telemetry streaming to the online ARKS War Room network.",
                    "bullets": [
                        "Automated cloud telemetry ensures instantaneous coordinate and contribution updates with minimal network overhead.",
                        "Client Version Security: Strictly verifies Version 7.1.0 to protect tactical leaderboard integrity.",
                        "Interactive Web War Room: Features Tactical Spotlight (highlight player holdings), Reactive Target Inspector, Top 10 Cyber Neon palette, and Operatives Roster (L/T).",
                        "Click '🪐 ARKS War Room (Web)' to open the live galaxy map in your browser.",
                    ],
                    "action_type": "open_web_war",
                    "action_text": "🪐 Open ARKS War Room (Web)",
                },
            ],
        },
        "community": {
            "title": "Discord Community & Official Credits",
            "cards": [
                {
                    "title": "🌸 NEKO★FAMILY PSO2:NGS Community",
                    "badge": "Official Community",
                    "badge_color": "#9C27B0",
                    "desc": "Join our vibrant PSO2:NGS community for team runs, farming guides, and tracker support!",
                    "bullets": [
                        "🤝 Connect with fellow ARKS operatives across Ship 4 JP and global servers.",
                        "🗺️ Real-time ARKS War Room galaxy sector coordination and team strategy.",
                        "💎 High-efficiency PSE Burst grinding routes, trigger groups, and drop spot intel.",
                        "🛠️ Prompt bug reporting, feature suggestions, and new version release announcements.",
                    ],
                    "credit_box": True,
                },
                {
                    "title": "📜 Official Project Attribution & Credit",
                    "badge": "Verified Attribution",
                    "badge_color": "#D81B60",
                    "desc": "This companion tracker utility is maintained and supported by the community.",
                    "bullets": [
                        "Project: NEKO Item & Meseta Tracker (PSO2:NGS)",
                        "Team: TEAM NEKO FAMILY SHIP 4 JP",
                        "Official Credit Line:",
                        "NEKO★FAMILY PSO2:NGS Community discord.gg/fkjXW9AJ6a",
                    ],
                    "credit_text": "NEKO★FAMILY PSO2:NGS Community discord.gg/fkjXW9AJ6a",
                },
            ],
        },
    },
    "th": {
        "tabs": [
            ("setup", "🚀 เริ่มต้นใช้งาน"),
            ("tracking", "💰 เมเซต้า & ไอเท็ม"),
            ("overlay", "🪟 โหมด Overlay"),
            ("war", "⚔️ ARKS War"),
            ("community", "🌸 ชุมชน & เครดิต"),
        ],
        "setup": {
            "title": "การเริ่มต้นใช้งาน & ตั้งค่าโฟลเดอร์ Log",
            "cards": [
                {
                    "title": "📂 1. วิธีเลือกโฟลเดอร์ Log เกม PSO2:NGS",
                    "badge": "จำเป็นสำหรับการใช้งาน",
                    "badge_color": "#0284C7",
                    "desc": "ตัวเกม PSO2:NGS จะบันทึกข้อมูลการรับเงินและไอเท็มดรอปทั้งหมดลงไฟล์ ActionLog โดยอัตโนมัติ",
                    "bullets": [
                        "ตำแหน่งโฟลเดอร์ Log มาตรฐานบน Windows:",
                        "Documents\\SEGA\\PHANTASYSTARONLINE2\\log_ngs",
                        "คลิกปุ่ม '📂 จิ้มเลือกโฟลเดอร์ Log' ที่แถบเมนูด้านซ้าย แล้วเลือกโฟลเดอร์ log_ngs",
                        "เมื่อเลือกสำเร็จ โปรแกรมจะเริ่มอ่านไฟล์ Log ล่าสุดแบบ Real-time ทันที",
                    ],
                    "path_box": "Documents\\SEGA\\PHANTASYSTARONLINE2\\log_ngs",
                    "action_type": "select_folder",
                    "action_text": "📂 เลือกโฟลเดอร์ Log ตอนนี้",
                },
                {
                    "title": "👤 2. สถาปัตยกรรม Zero-Login (ไม่ใช้รหัสผ่าน)",
                    "badge": "ปลอดภัย 100% / ไม่ต้องสมัคร",
                    "badge_color": "#10B981",
                    "desc": "โปรแกรมให้ความสำคัญกับความปลอดภัยและความเป็นส่วนตัวของคุณเป็นอันดับหนึ่ง",
                    "bullets": [
                        "Zero-Login: ตรวจจับชื่อตัวละครและรหัสผู้เล่นจริงจากไฟล์ Log ในเครื่องโดยอัตโนมัติ",
                        "ไม่ต้องกรอกรหัสผ่าน: ไม่มีการขอ ไม่มีการจัดเก็บ และไม่มีการส่ง SEGA ID หรือรหัสผ่านใดๆ",
                        "สลับตัวละครสะดวก: เมื่อเปลี่ยนตัวละครในเกม ระบบจะอัปเดตชื่อใหม่อัตโนมัติทันที",
                    ],
                },
                {
                    "title": "🛡️ 3. มาตรฐาน 100% TOS Safe (ปลอดภัยจากการแบน)",
                    "badge": "ปลอดภัยจาก Anti-Cheat",
                    "badge_color": "#8B5CF6",
                    "desc": "ออกแบบตามกฎและข้อตกลงผู้ใช้งานอย่างเคร่งครัด ไร้ความเสี่ยงต่อการโดนแบน",
                    "bullets": [
                        "อ่านเฉพาะไฟล์ข้อความภายนอก: มอนิเตอร์ไฟล์ ActionLog.txt ที่เกมสร้างไว้เท่านั้น",
                        "ไม่แตะต้อง Memory ของเกม: ไม่ใช้ OpenProcess / ReadProcessMemory ใดๆ ทั้งสิ้น",
                        "ไม่มีการฉีด DLL (Zero Injection): ไม่มีการ Hook API หรือดัดแปลงไฟล์เกมใดๆ",
                        "Anti-Tamper ในตัว: ตรวจสอบความถูกต้องของลำดับเหตุการณ์ เวลา และเพดานเงินดรอป",
                    ],
                },
            ],
        },
        "tracking": {
            "title": "การติดตามเงินเมเซต้า & รายการไอเท็มดรอป",
            "cards": [
                {
                    "title": "💎 1. ยอดเงินรอบนี้ & อัตราความเร็ว (M/hr)",
                    "badge": "คำนวณสด Real-time",
                    "badge_color": "#D81B60",
                    "desc": "ติดตามการเติบโตของเงิน N-Meseta ขณะฟาร์ม PSE Burst และบอส Triggers",
                    "bullets": [
                        "ยอดเงินรอบนี้ (Session): เงิน N-Meseta สุทธิที่ได้รับจากการเก็บเงิน ขายของ และเควสต์",
                        "เงินในกระเป๋า (Wallet): ยอดเงินคงเหลือปัจจุบันในตัวละครแบบสดๆ",
                        "ความเร็ว (M/hr): อัตราความเร็วในการหาเงินต่อชั่วโมง คำนวณตามเวลาที่ใช้ฟาร์มจริง",
                        "First-Drop Inception: นาฬิกาจะเริ่มนับเวลาเมื่อมีเงินหรือไอเท็มชิ้นแรกดรอปจริง ทำให้เวลาว่างในล็อบบี้ไม่ดึงสถิติ M/hr ของคุณให้ต่ำลง",
                    ],
                },
                {
                    "title": "📦 2. รายการของดรอป & กล่องค้นหา",
                    "badge": "จัดการไอเท็มดรอป",
                    "badge_color": "#0284C7",
                    "desc": "แสดงรายการไอเท็ม อุปกรณ์ แคปซูล และวัตถุดิบทั้งหมดที่ได้รับพร้อมจำนวน",
                    "bullets": [
                        "กล่องค้นหา (Search): ค้นหาชื่อไอเท็มทันใจ เช่น 'Astraea', 'Refiner', 'Dualble'",
                        "รวมยอดอัตโนมัติ: ของที่ดรอปซ้ำจะแสดงจำนวนสะสมพร้อมป้ายบอกจำนวนอย่างชัดเจน",
                    ],
                },
                {
                    "title": "🎯 3. ระบบฟิลเตอร์ Watch List",
                    "badge": "โฟกัสเฉพาะของหายาก",
                    "badge_color": "#EC4899",
                    "desc": "เลือกดูเฉพาะไอเท็มราคาแพงหรือแคปซูลที่ต้องการ และซ่อนขยะที่ไม่ต้องการ",
                    "bullets": [
                        "คลิกปุ่ม 'Edit Watch List' เพื่อใส่ชื่อไอเท็มที่ต้องการติดตาม (บรรทัดละ 1 ชื่อ)",
                        "เปิดสวิตช์ 'เปิดใช้ Watch List Filter': รายการของดรอปและหน้าต่าง Overlay จะแสดงเฉพาะไอเท็มที่คุณโฟกัส",
                    ],
                },
                {
                    "title": "🔄 4. การเริ่มนับใหม่ (Reset)",
                    "badge": "เริ่มรอบใหม่",
                    "badge_color": "#6B7280",
                    "desc": "เริ่มต้นเซสชันใหม่เมื่อเปลี่ยนพื้นที่ฟาร์มหรือเข้าปาร์ตี้ใหม่",
                    "bullets": [
                        "คลิกปุ่ม 'เริ่มนับใหม่ (Reset)' เพื่อล้างยอดเงิน เวลา และรายการของดรอปทั้งหมด",
                        "ระบบจะเลื่อนตัวอ่านไฟล์ไปที่ตำแหน่งล่าสุด เพื่อไม่ให้นำข้อมูลเก่ากลับมานับซ้ำ",
                    ],
                },
            ],
        },
        "overlay": {
            "title": "โหมด Gadget (หน้าต่างลอยทับหน้าจอเกม)",
            "cards": [
                {
                    "title": "🖥️ 1. Full Overlay (Item & Meseta)",
                    "badge": "ครบทุกข้อมูลสำคัญ",
                    "badge_color": "#FF69B4",
                    "desc": "หน้าต่าง Overlay โปร่งใส ลอยอยู่เหนือเกมตลอดเวลาโดยไม่บดบังมุมมอง",
                    "bullets": [
                        "แสดงยอดเงิน Meseta รวม, เงินในกระเป๋า, เวลาที่ฟาร์ม, และอัตราความเร็ว M/hr",
                        "แสดงรายการไอเท็มดรอปล่าสุด 4 รายการ พร้อมป้ายจำนวน",
                        "Always-on-top: ลอยทับหน้าจอเกมโหมด Borderless Windowed ได้อย่างสมบูรณ์แบบ",
                        "คลิกเปิด/ปิดได้จากปุ่ม 'Item & Meseta' ที่แถบเมนู",
                    ],
                },
                {
                    "title": "⚡ 2. Mini Overlay (เฉพาะตัวเลข Meseta)",
                    "badge": "กะทัดรัด ไม่เกะกะ",
                    "badge_color": "#F06292",
                    "desc": "ขนาดเล็กกะทัดรัดพิเศษ ออกแบบสำหรับการต่อสู้อย่างจริงจัง",
                    "bullets": [
                        "แสดงเฉพาะยอดเงินรอบนี้และเงินในกระเป๋าด้วยแถบตัวเลขคมชัด สวยงาม",
                        "ระบบ Dynamic Bounds ปรับความสูงอัตโนมัติ ป้องกันข้อความตกหล่นบนจอทุก DPI Scaling",
                        "คลิกเปิด/ปิดได้จากปุ่ม 'Meseta' ที่แถบเมนู",
                    ],
                },
                {
                    "title": "🖱️ 3. การลากย้ายตำแหน่งหน้าต่าง",
                    "badge": "ปรับแต่งตามใจชอบ",
                    "badge_color": "#8B5CF6",
                    "desc": "จัดวางหน้าต่างให้อยู่ในตำแหน่งที่ถนัดที่สุดตามเลย์เอาต์หน้าจอเกมของคุณ",
                    "bullets": [
                        "คลิกเมาส์ซ้ายค้างที่แถบด้านบนของหน้าต่าง Overlay แล้วลากไปวางได้ทุกจุดบนหน้าจอ",
                        "รองรับการใช้งานหลายหน้าจอ (Multi-Monitor Setup)",
                    ],
                },
            ],
        },
        "war": {
            "title": "โหมดสงครามออนไลน์ ARKS War Room (Coordinate War V9)",
            "cards": [
                {
                    "title": "⚔️ 1. กฎกติกาการยึดช่อง ('ใครใส่เยอะคนนั้นเป็นเจ้าของ')",
                    "badge": "ระบบ V9 หลัก",
                    "badge_color": "#3B82F6",
                    "desc": "กฎเหล็กหลัก: 'เกมแค่เติมเงินเข้าไปในช่อง ใครใส่เยอะคนนั้นเป็นเจ้าของ' (ระบบ V9 Release)",
                    "bullets": [
                        "คลิกปุ่ม '⚔️ เข้าสู่สงคราม (ARKS War)' ที่แถบเมนูเพื่อเข้าสู่หน้าจอสงคราม",
                        "ตารางพิกัดครอบคลุม 798 Sectors: แกน X [-12..25], แกน Y [-11..9]",
                        "แต่ละ Sector แบ่งออกเป็น 4 ช่องย่อย Quadrant (#1 NW, #2 NE, #3 SW, #4 SE) ขนาดช่องละ 300x300px",
                        "มูลค่าตั้งต้นก่อนยึด 10M: แต่ละช่องย่อยมีเกณฑ์ปลดล็อกที่ 10,000,000 N-Meseta (10M ℳ)",
                        "การชิงพื้นที่ (Clash): ใครที่เติมเงินฟาร์มใส่ช่องนั้นเกิน 10M และมียอดสูงสุดจะได้เป็นเจ้าของทันที หากมีใครใส่เงินแซง สิทธิ์จะถูกแย่งทันที!",
                        "ปลดแอก Sector สมบูรณ์ (40M ℳ): ยึดครองครบทั้ง 4 ช่องย่อยในเซกเตอร์",
                        "หลอมรวมผืนแผ่นดิน (Seamless Continent): หากทั้ง 4 ช่องเป็นของผู้เล่นคนเดียวกัน เส้นแบ่งจะหายไปและกลายเป็นผืนดินเรืองแสงผืนเดียว",
                    ],
                },
                {
                    "title": "📋 2. ระบบวางพิกัดอัจฉริยะ & พิกัดสำคัญ (Landmarks)",
                    "badge": "วางปุ๊บ ติดปั๊บ",
                    "badge_color": "#10B981",
                    "desc": "คัดลอกพิกัดเป้าหมายจากเว็บสงครามแล้ววางลงโปรแกรมได้ทันที",
                    "bullets": [
                        "คัดลอกพิกัดจากหน้าเว็บแล้วคลิกปุ่ม '📋 วาง' (รองรับรูปแบบ '15, -6, 2', '[15, -6, 2]' ฯลฯ)",
                        "เลือกพิกัดสำคัญได้ง่ายๆ จากเมนู Landmark: Core [0, 0], NGS [3, 3], Earth [9, -3], Sun [8, -3] ฯลฯ",
                        "คลิกปุ่ม '💾 บันทึก' เพื่อล็อกพิกัดเป้าหมายสำหรับการซิงค์ข้อมูล",
                        "สถานะพร้อมรบ (Standby Presence): แม้จะมียอดเงิน 0 ℳ การต่อพิกัดจะแสดงตัวละครในทำเนียบนักรบพร้อมสัญลักษณ์ 📍 พร้อมรบสดทันที",
                    ],
                },
                {
                    "title": "⚡ 3. การซิงค์สดออนไลน์ & ฟีเจอร์หน้าเว็บ War Room",
                    "badge": "ซิงค์อัตโนมัติ 60fps",
                    "badge_color": "#F59E0B",
                    "desc": "ส่งข้อมูลสถิติและพิกัดการรบสดขึ้นระบบคลาวด์ War Room แบบเรียลไทม์",
                    "bullets": [
                        "ระบบส่งข้อมูลสดอัตโนมัติ ช่วยให้ผลการยึดครองอัปเดตทันใจและประหยัดอินเทอร์เน็ต",
                        "คุ้มครองความปลอดภัยและความเป็นธรรมด้วยระบบ Client Version Security (บังคับใช้เวอร์ชัน 7.1.0)",
                        "หน้าเว็บ Tactical Observability: มีระบบ Tactical Spotlight (ส่องสว่างทั่วทั้งดาราจักรเมื่อคลิกชื่อผู้เล่น), Reactive Inspector, และสี Cyber Neon สำหรับ Top 10",
                        "คลิกปุ่ม '🪐 ARKS War Room (Web)' เพื่อเปิดดูแผนที่สงครามสดบนเว็บเบราว์เซอร์ของคุณ",
                    ],
                    "action_type": "open_web_war",
                    "action_text": "🪐 เปิดหน้าเว็บ ARKS War Room",
                },
            ],
        },
        "community": {
            "title": "ดิสคอร์ดคอมมูนิตี้ & เครดิตทางการ",
            "cards": [
                {
                    "title": "🌸 NEKO★FAMILY PSO2:NGS Community",
                    "badge": "คอมมูนิตี้ทางการ",
                    "badge_color": "#9C27B0",
                    "desc": "เข้าร่วมคอมมูนิตี้คนเล่น PSO2:NGS แลกเปลี่ยนเทคนิคการฟาร์ม และร่วมกิจกรรมทีมสุดมันส์!",
                    "bullets": [
                        "🤝 พบปะและร่วมเล่นกับเพื่อนๆ สมาชิก ARKS ทั้งใน Ship 4 JP และเซิร์ฟเวอร์ Global",
                        "🗺️ วางแผนและสั่งการยึดพื้นที่กาแล็กซีในโหมด ARKS War Room แบบ Real-time",
                        "💎 แชร์จุดฟาร์ม PSE Burst เทคนิคทำเงินไว และข้อมูลแหล่งดรอปไอเท็มหายาก",
                        "🛠️ แจ้งปัญหา แนะนำฟีเจอร์ใหม่ พูดคุยกับทีมพัฒนา และอัปเดตเวอร์ชันล่าสุดได้ก่อนใคร",
                    ],
                    "credit_box": True,
                },
                {
                    "title": "📜 เครดิตและสิทธิ์การพัฒนา (Attribution)",
                    "badge": "การรับรองทางการ",
                    "badge_color": "#D81B60",
                    "desc": "โปรแกรมติดตามไอเท็มและเมเซต้านี้ได้รับการพัฒนาและดูแลโดยคอมมูนิตี้",
                    "bullets": [
                        "ชื่อโปรแกรม: NEKO Item & Meseta Tracker (PSO2:NGS)",
                        "ทีมผู้พัฒนา: TEAM NEKO FAMILY SHIP 4 JP",
                        "เครดิตทางการ:",
                        "NEKO★FAMILY PSO2:NGS Community discord.gg/fkjXW9AJ6a",
                    ],
                    "credit_text": "NEKO★FAMILY PSO2:NGS Community discord.gg/fkjXW9AJ6a",
                },
            ],
        },
    },
    "ja": {
        "tabs": [
            ("setup", "🚀 初期設定＆ログ"),
            ("tracking", "💰 メセタ＆アイテム"),
            ("overlay", "🪟 ガジェットオーバーレイ"),
            ("war", "⚔️ ARKS War 作戦"),
            ("community", "🌸 コミュニティ＆謝辞"),
        ],
        "setup": {
            "title": "初期設定とログフォルダの指定",
            "cards": [
                {
                    "title": "📂 1. PSO2:NGS ログフォルダの選択方法",
                    "badge": "初期設定必須",
                    "badge_color": "#0284C7",
                    "desc": "ゲームプレイ中に獲得したメセタやアイテムドロップは、ゲームクライアントにより自動的にActionLogへ保存されます。",
                    "bullets": [
                        "Windowsでの標準ログ保存先パス:",
                        "Documents\\SEGA\\PHANTASYSTARONLINE2\\log_ngs",
                        "左メニューの「📂 ログフォルダを選択」を押し、上記の log_ngs フォルダを指定します。",
                        "指定完了後、トラッカーがリアルタイムで最新のログを自動追跡します。",
                    ],
                    "path_box": "Documents\\SEGA\\PHANTASYSTARONLINE2\\log_ngs",
                    "action_type": "select_folder",
                    "action_text": "📂 今すぐログフォルダを選択",
                },
                {
                    "title": "👤 2. Zero-Login（アカウント不要）設計",
                    "badge": "プライバシー保護 / 登録不要",
                    "badge_color": "#10B981",
                    "desc": "本ツールはセキュリティとプライバシーを最重要事項として設計されています。",
                    "bullets": [
                        "Zero-Login: ログファイルから現在のキャラクター名とプレイヤーIDを自動判別。",
                        "パスワード入力一切不要: SEGA IDやパスワードを要求・保存・送信することは絶対にありません。",
                        "キャラクター切替自動追従: ゲーム内でキャラを変更した場合も、自動で検知して統計を引き継ぎます。",
                    ],
                },
                {
                    "title": "🛡️ 3. 100% 規約遵守・安全設計 (TOS Safe)",
                    "badge": "BANリスクゼロ",
                    "badge_color": "#8B5CF6",
                    "desc": "利用規約を遵守した完全非侵入型設計により、安心してご使用いただけます。",
                    "bullets": [
                        "外部テキストログのみ監視: ディスク上のActionLogテキストのみを受動的に監視。",
                        "ゲームメモリ非接触: OpenProcessやReadProcessMemory等の危険なAPIは一切使用しません。",
                        "DLLインジェクション皆無: DirectXフックやキーロガー等の不正挙動は一切ありません。",
                        "多層改ざん検知エンジン: タイムスタンプの整合性や獲得速度の上限を自動監査。",
                    ],
                },
            ],
        },
        "tracking": {
            "title": "獲得メセタとドロップアイテムの追跡",
            "cards": [
                {
                    "title": "💎 1. 今回の獲得メセタ＆時給効率 (M/hr)",
                    "badge": "リアルタイム算出",
                    "badge_color": "#D81B60",
                    "desc": "PSEバースト周回やトリガーボス戦での稼ぎを正確にモニタリング。",
                    "bullets": [
                        "セッション獲得メセタ: ドロップ拾得、自動売却、クエスト報酬による純獲得額。",
                        "現在の所持メセタ: ゲーム内の最新所持メセタ残高をリアルタイム表示。",
                        "獲得時給 (M/hr): 実稼働時間に基づき、リアルタイムで時間あたりの獲得速度を算出。",
                        "初回ドロップ時タイマースタート: ロビーでの放置時間で時給が下がるのを防ぐため、最初のドロップが発生した瞬間から計測を開始します。",
                    ],
                },
                {
                    "title": "📦 2. ドロップアイテム一覧＆即座検索",
                    "badge": "ドロップ管理",
                    "badge_color": "#0284C7",
                    "desc": "入手した装備、特殊能力カプセル、素材アイテムを個数・時間とともに記録。",
                    "bullets": [
                        "検索バー: 「アストレア」「リファイナー」等の名前で即座に絞り込み検索可能。",
                        "自動数量集計: 同一アイテムのドロップは自動で個数バッジとして集約表示されます。",
                    ],
                },
                {
                    "title": "🎯 3. ウォッチリストフィルター機能",
                    "badge": "レアアイテム集中監視",
                    "badge_color": "#EC4899",
                    "desc": "高額ドロップや注目カプセルのみを強調し、不要なドロップを非表示にできます。",
                    "bullets": [
                        "「ウォッチリスト編集」ボタンから、監視したいアイテム名を登録（1行に1つ）。",
                        "「ウォッチリストフィルター有効」スイッチをONにすると、指定したアイテムのみが表示されます。",
                    ],
                },
                {
                    "title": "🔄 4. セッションリセット (Reset)",
                    "badge": "新たな周回開始",
                    "badge_color": "#6B7280",
                    "desc": "周回場所の変更や新しいパーティでの開始時にいつでもリセット可能。",
                    "bullets": [
                        "「リセット (Reset)」ボタンを押すと、獲得メセタ、経過時間、ドロップ履歴が初期化されます。",
                        "ログ読み取り位置を末尾（EOF）へ移動するため、過去のドロップが混入することはありません。",
                    ],
                },
            ],
        },
        "overlay": {
            "title": "ガジェットモード (ゲーム画面最前面オーバーレイ)",
            "cards": [
                {
                    "title": "🖥️ 1. フルオーバーレイ (Item & Meseta)",
                    "badge": "フルスペックHUD",
                    "badge_color": "#FF69B4",
                    "desc": "戦闘中も邪魔にならない半透明設計で、ゲーム画面の上に常時最前面表示。",
                    "bullets": [
                        "獲得メセタ、所持メセタ、周回時間、獲得時給 (M/hr) を一覧表示。",
                        "直近にドロップした最新4アイテムを個数バッジ付きで表示。",
                        "Always-on-top: 仮想フルスクリーン（ボーダーレス）のゲーム画面上に常時浮遊表示。",
                        "サイドバーの「Item & Meseta」ボタンからワンクリックで開閉できます。",
                    ],
                },
                {
                    "title": "⚡ 2. ミニオーバーレイ (メセタ専用)",
                    "badge": "省スペースカウンター",
                    "badge_color": "#F06292",
                    "desc": "戦闘視界を一切遮らない超小型のメセタカウンター。",
                    "bullets": [
                        "今回の獲得メセタと所持メセタのみをスリムなバーにコンパクト表示。",
                        "動的サイズ自動調整により、WindowsのDPIスケーリング設定に関わらず文字切れを防ぎます。",
                        "サイドバーの「Meseta」ボタンからワンクリックで開閉できます。",
                    ],
                },
                {
                    "title": "🖱️ 3. ウィンドウのドラッグ移動",
                    "badge": "自由なレイアウト",
                    "badge_color": "#8B5CF6",
                    "desc": "ゲーム内のUI配置に合わせて、オーバーレイを好きな場所へ移動できます。",
                    "bullets": [
                        "オーバーレイ上部のヘッダーバーを左クリックしたままドラッグすることで自由に配置可能。",
                        "マルチモニター環境でも好きな画面へ配置できます。",
                    ],
                },
            ],
        },
        "war": {
            "title": "オンライン作戦室 ARKS War Room モード (Coordinate War V9)",
            "cards": [
                {
                    "title": "⚔️ 1. 座標スロット制圧戦 (「多く入れた者が占有者」)",
                    "badge": "V9基幹ルール",
                    "badge_color": "#3B82F6",
                    "desc": "コアルール: 『スロットにメセタを投入し、10M超えで最も多く入れた者が占有者となる』(V9 Release)",
                    "bullets": [
                        "サイドバーの「⚔️ 作戦参加 (ARKS War)」ボタンで作戦室画面に切り替わります。",
                        "銀河グリッド全798セクター展開: セクターX [-12..25]、セクターY [-11..9]。",
                        "各セクターは4つの象限スロットに分割 (#1 NW, #2 NE, #3 SW, #4 SE)。",
                        "占有閾値 10M: 各スロットは 10,000,000 N-メセタ (10M ℳ) の投入で占有権を獲得。",
                        "占有権強奪 (Clash): 他プレイヤーがそのスロットにさらに多くのメセタを投入した場合、即座に占有権が交代します！",
                        "セクター完全解放 (40M ℳ): セクター内全4スロットの制圧でセクター完全解放。",
                        "シームレス大陸化: 4スロットすべてを同一プレイヤーが制圧すると、内部境界線が消滅して1つの巨大ネオン領土に統合されます。",
                    ],
                },
                {
                    "title": "📋 2. スマート座標解析＆主要拠点プリセット",
                    "badge": "ワンクリック同期",
                    "badge_color": "#10B981",
                    "desc": "Web戦況マップで指定された作戦座標を素早く入力可能。",
                    "bullets": [
                        "Web画面から座標をコピーし、「📋 貼付」ボタンを押すだけで自動解析（'15, -6, 2' 等に対応）。",
                        "主要拠点プリセット（Core [0, 0], NGS [3, 3], 地球 [9, -3], 太陽 [8, -3] 等）から選択も可能。",
                        "「💾 保存」ボタンで作戦座標をロックし、テレメトリ同期を開始します。",
                        "スタンバイ出撃可視化: 0 ℳであってもTrackerを接続すると作戦名簿に 📍 スタンバイ状態として即座に可視化されます。",
                    ],
                },
                {
                    "title": "⚡ 3. クラウドリアルタイム同期＆Web戦況マップHUD",
                    "badge": "リアルタイム 60fps",
                    "badge_color": "#F59E0B",
                    "desc": "獲得貢献度を作戦サーバーへ安全かつリアルタイムに自動同期。",
                    "bullets": [
                        "自動クラウド同期により、ネットワーク負荷を最小限に抑えつつ瞬時に戦況を反映。",
                        "クライアントバージョンセキュリティ機構（Version 7.1.0 厳格適用）により公正性を保護。",
                        "Web戦況マップ機能: 戦術スポットライト (プレイヤー領土の全銀河強調ハイライト)、リアクティブ・インスペクター、Top 10 サイバーネオンパレット。",
                        "「🪐 ARKS War Room (Web)」ボタンをクリックしてブラウザで銀河全体の戦況を閲覧可能。",
                    ],
                    "action_type": "open_web_war",
                    "action_text": "🪐 ARKS War Room (Web) を開く",
                },
            ],
        },
        "community": {
            "title": "公式Discordコミュニティ＆クレジット",
            "cards": [
                {
                    "title": "🌸 NEKO★FAMILY PSO2:NGS Community",
                    "badge": "公式コミュニティ",
                    "badge_color": "#9C27B0",
                    "desc": "PSO2:NGSプレイヤーが集う公式コミュニティへようこそ！",
                    "bullets": [
                        "🤝 Ship 4 JPおよびグローバルサーバーのアークス仲間と繋がろう！",
                        "🗺️ ARKS War Roomの銀河制圧作戦をチームメンバーとリアルタイム連携。",
                        "💎 高効率PSEバースト周回ルート、トリガー連戦、レアドロップ情報の共有。",
                        "🛠️ 不具合報告、機能改善要望、最新アップデート情報の最速配信。",
                    ],
                    "credit_box": True,
                },
                {
                    "title": "📜 開発クレジットと著作権表示 (Attribution)",
                    "badge": "公式クレジット",
                    "badge_color": "#D81B60",
                    "desc": "本トラッカーツールはコミュニティ有志によって開発・保守されています。",
                    "bullets": [
                        "プロジェクト名: NEKO Item & Meseta Tracker (PSO2:NGS)",
                        "開発チーム: TEAM NEKO FAMILY SHIP 4 JP",
                        "公式クレジット表示:",
                        "NEKO★FAMILY PSO2:NGS Community discord.gg/fkjXW9AJ6a",
                    ],
                    "credit_text": "NEKO★FAMILY PSO2:NGS Community discord.gg/fkjXW9AJ6a",
                },
            ],
        },
    },
}


class GuideWindow(ctk.CTkToplevel):
    """
    Modern 3-Language User Guide (How-To-Use) Window.
    Provides category tab navigation, live language switching,
    direct Discord integration, and official community credit.
    """

    def __init__(self, parent: Any, initial_tab: str = "setup") -> None:
        super().__init__(parent)
        self.app = parent
        self.current_tab = initial_tab

        # Window styling
        self.overrideredirect(True)
        self.geometry("740x620")
        self.configure(fg_color="#FFFFFF")
        self.attributes("-topmost", True)
        self.transient(parent)

        # Center relative to parent window
        self.center_window()

        # Keyboard shortcuts
        self.bind("<Escape>", lambda e: self.destroy())

        # Build UI layout
        self.build_ui()

        # Subscribe to language changes
        self._on_lang_sub = self._on_language_changed_event
        event_bus.subscribe("language_changed", self._on_lang_sub)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def center_window(self) -> None:
        try:
            self.update_idletasks()
            pw = self.app.winfo_width() if self.app.winfo_width() > 100 else 950
            ph = self.app.winfo_height() if self.app.winfo_height() > 100 else 620
            px = self.app.winfo_x()
            py = self.app.winfo_y()
            w, h = 740, 620
            x = max(0, px + (pw - w) // 2)
            y = max(0, py + (ph - h) // 2)
            self.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            self.geometry("740x620+150+100")

    def build_ui(self) -> None:
        # 1. Custom Pink Header Bar
        self.header_bar = ctk.CTkFrame(self, height=42, corner_radius=0, fg_color=COLOR_PINK_HEADER)
        self.header_bar.pack(fill="x", side="top")
        self.header_bar.pack_propagate(False)

        # Logo / Icon
        if os.path.exists(ICON_FILENAME):
            try:
                img = Image.open(ICON_FILENAME)
                self.icon_ctk = ctk.CTkImage(img, size=(22, 22))
                self.lbl_icon = ctk.CTkLabel(self.header_bar, text="", image=self.icon_ctk)
                self.lbl_icon.pack(side="left", padx=(12, 6))
            except Exception:
                pass

        self.lbl_title = ctk.CTkLabel(
            self.header_bar,
            text=t("dialog_guide_title"),
            font=(FONT_FAMILY, 13, "bold"),
            text_color="#333333",
        )
        self.lbl_title.pack(side="left", padx=4)

        # Close button (✕)
        self.btn_close = ctk.CTkButton(
            self.header_bar,
            text="✕",
            width=36,
            height=36,
            corner_radius=0,
            fg_color="transparent",
            text_color="#D81B60",
            hover_color="#FFE4E1",
            font=("Arial", 14, "bold"),
            command=self.destroy,
        )
        self.btn_close.pack(side="right", padx=6)

        # Language Selector Segmented Button in Header
        self.seg_lang = ctk.CTkSegmentedButton(
            self.header_bar,
            values=["EN", "TH", "JA"],
            height=26,
            font=(FONT_FAMILY, 10, "bold"),
            selected_color=COLOR_PINK_ACCENT,
            selected_hover_color="#D81B60",
            unselected_color="#F8F8F8",
            unselected_hover_color="#E8E8E8",
            text_color=COLOR_TEXT_MAIN,
            corner_radius=UI_RADIUS,
            command=self._on_lang_switch_clicked,
        )
        self.seg_lang.set(i18n.get_button_label())
        self.seg_lang.pack(side="right", padx=(0, 10))

        self.lbl_lang_hint = ctk.CTkLabel(
            self.header_bar,
            text="🌐",
            font=(FONT_FAMILY, 12),
            text_color="#444444",
        )
        self.lbl_lang_hint.pack(side="right", padx=(0, 4))

        # Make header draggable
        def start_move(event):
            self._drag_x = event.x
            self._drag_y = event.y

        def do_move(event):
            try:
                x = self.winfo_x() + (event.x - self._drag_x)
                y = self.winfo_y() + (event.y - self._drag_y)
                self.geometry(f"+{x}+{y}")
            except Exception:
                pass

        self.header_bar.bind("<ButtonPress-1>", start_move)
        self.header_bar.bind("<B1-Motion>", do_move)
        self.lbl_title.bind("<ButtonPress-1>", start_move)
        self.lbl_title.bind("<B1-Motion>", do_move)

        # 2. Navigation Tabs Bar
        self.nav_frame = ctk.CTkFrame(self, height=44, fg_color="#FDF2F4", corner_radius=0)
        self.nav_frame.pack(fill="x", side="top")
        self.nav_frame.pack_propagate(False)

        # Segmented tab buttons
        lang = i18n.current_language
        tab_defs = GUIDE_SECTIONS.get(lang, GUIDE_SECTIONS["en"])["tabs"]
        self.tab_keys = [t_id for t_id, _ in tab_defs]
        self.tab_labels = [label for _, label in tab_defs]
        self.tab_map = dict(tab_defs)
        self.tab_rev_map = {label: t_id for t_id, label in tab_defs}

        self.seg_tabs = ctk.CTkSegmentedButton(
            self.nav_frame,
            values=self.tab_labels,
            height=32,
            font=(FONT_FAMILY, 11, "bold"),
            selected_color=COLOR_PINK_ACCENT,
            selected_hover_color="#D81B60",
            unselected_color="#FFFFFF",
            unselected_hover_color="#FCE7F3",
            text_color=COLOR_TEXT_MAIN,
            corner_radius=UI_RADIUS,
            command=self._on_tab_selected,
        )
        # Select initial tab
        init_label = self.tab_map.get(self.current_tab, self.tab_labels[0])
        self.seg_tabs.set(init_label)
        self.seg_tabs.pack(fill="x", padx=12, pady=6)

        # 3. Persistent Bottom Credit & Action Bar
        self.footer_frame = ctk.CTkFrame(self, height=52, fg_color="#FFF1F2", corner_radius=0)
        self.footer_frame.pack(fill="x", side="bottom")
        self.footer_frame.pack_propagate(False)

        # Community Credit Label on Left
        self.lbl_credit_footer = ctk.CTkLabel(
            self.footer_frame,
            text=f"🌸 {DISCORD_CREDIT_FULL}",
            font=(FONT_FAMILY, 11, "bold"),
            text_color="#9C27B0",
        )
        self.lbl_credit_footer.pack(side="left", padx=15, pady=8)

        # Toast notification label (hidden by default)
        self.lbl_toast = ctk.CTkLabel(
            self.footer_frame,
            text="",
            font=(FONT_FAMILY, 11, "bold"),
            text_color="#10B981",
        )
        self.lbl_toast.pack(side="left", padx=5, pady=8)

        # Right side action buttons: Copy Link & Join Discord
        self.btn_join_discord_footer = ctk.CTkButton(
            self.footer_frame,
            text=t("btn_discord"),
            font=(FONT_FAMILY, 11, "bold"),
            fg_color=COLOR_DISCORD,
            hover_color="#7B1FA2",
            text_color="white",
            height=32,
            corner_radius=UI_RADIUS,
            command=self.open_discord,
        )
        self.btn_join_discord_footer.pack(side="right", padx=(4, 15), pady=8)

        self.btn_copy_link_footer = ctk.CTkButton(
            self.footer_frame,
            text=t("guide_btn_copy_link"),
            font=(FONT_FAMILY, 11),
            fg_color="#FFFFFF",
            hover_color="#F3E8FF",
            text_color="#4A044E",
            border_width=1,
            border_color="#E9D5FF",
            height=32,
            corner_radius=UI_RADIUS,
            command=self.copy_discord_link,
        )
        self.btn_copy_link_footer.pack(side="right", padx=(0, 4), pady=8)

        # 4. Scrollable Content Body
        self.scroll_body = ctk.CTkScrollableFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=0,
        )
        self.scroll_body.pack(fill="both", expand=True, padx=10, pady=(6, 4))

        # Render active tab
        self.render_tab_content(self.current_tab)

    def _on_tab_selected(self, selected_label: str) -> None:
        tab_id = self.tab_rev_map.get(selected_label, "setup")
        self.current_tab = tab_id
        self.render_tab_content(tab_id)

    def _on_lang_switch_clicked(self, lang_label: str) -> None:
        if hasattr(self.app, "set_app_language"):
            self.app.set_app_language(lang_label.lower())
        else:
            i18n.set_language(lang_label.lower())
            self.retranslate_ui()

    def _on_language_changed_event(self, language: str = "", **kwargs: Any) -> None:
        try:
            self.retranslate_ui()
        except Exception:
            pass

    def _on_close(self) -> None:
        try:
            event_bus.unsubscribe("language_changed", self._on_lang_sub)
        except Exception:
            pass
        self.destroy()

    def retranslate_ui(self) -> None:
        """Dynamically retranslate all labels, tabs, and active cards in-flight."""
        try:
            lang = i18n.current_language

            # Title and header
            self.lbl_title.configure(text=t("dialog_guide_title"))
            self.seg_lang.set(i18n.get_button_label())

            # Update tabs
            tab_defs = GUIDE_SECTIONS.get(lang, GUIDE_SECTIONS["en"])["tabs"]
            self.tab_keys = [t_id for t_id, _ in tab_defs]
            self.tab_labels = [label for _, label in tab_defs]
            self.tab_map = dict(tab_defs)
            self.tab_rev_map = {label: t_id for t_id, label in tab_defs}

            self.seg_tabs.configure(values=self.tab_labels)
            cur_label = self.tab_map.get(self.current_tab, self.tab_labels[0])
            self.seg_tabs.set(cur_label)

            # Footer
            self.lbl_credit_footer.configure(text=f"🌸 {DISCORD_CREDIT_FULL}")
            self.btn_join_discord_footer.configure(text=t("btn_discord"))
            self.btn_copy_link_footer.configure(text=t("guide_btn_copy_link"))

            # Re-render active tab content
            self.render_tab_content(self.current_tab)
        except Exception:
            pass

    def render_tab_content(self, tab_id: str) -> None:
        """Render card list for selected tab."""
        # Clear existing children
        for widget in self.scroll_body.winfo_children():
            widget.destroy()

        lang = i18n.current_language
        content_dict = GUIDE_SECTIONS.get(lang, GUIDE_SECTIONS["en"])
        tab_data = content_dict.get(tab_id, content_dict.get("setup", {}))
        cards = tab_data.get("cards", [])

        for idx, card in enumerate(cards):
            card_frame = ctk.CTkFrame(
                self.scroll_body,
                fg_color="#FFF8FA",
                border_color="#FCE7F3",
                border_width=1,
                corner_radius=8,
            )
            card_frame.pack(fill="x", padx=6, pady=(4, 8))

            # Header row of card (Title + Badge)
            hdr_row = ctk.CTkFrame(card_frame, fg_color="transparent")
            hdr_row.pack(fill="x", padx=12, pady=(10, 4))

            title_lbl = ctk.CTkLabel(
                hdr_row,
                text=card.get("title", ""),
                font=(FONT_FAMILY, 13, "bold"),
                text_color="#D81B60",
                anchor="w",
            )
            title_lbl.pack(side="left", fill="x", expand=True)

            badge_text = card.get("badge")
            if badge_text:
                badge_bg = card.get("badge_color", "#0284C7")
                badge_lbl = ctk.CTkLabel(
                    hdr_row,
                    text=f" {badge_text} ",
                    font=(FONT_FAMILY, 10, "bold"),
                    fg_color=badge_bg,
                    text_color="white",
                    corner_radius=4,
                    height=20,
                )
                badge_lbl.pack(side="right", padx=(5, 0))

            # Description
            desc_text = card.get("desc")
            if desc_text:
                desc_lbl = ctk.CTkLabel(
                    card_frame,
                    text=desc_text,
                    font=(FONT_FAMILY, 11),
                    text_color=COLOR_TEXT_MAIN,
                    justify="left",
                    anchor="w",
                    wraplength=660,
                )
                desc_lbl.pack(fill="x", padx=14, pady=(2, 6))

            # Path box if provided
            path_val = card.get("path_box")
            if path_val:
                pbox = ctk.CTkFrame(card_frame, fg_color="#F3F4F6", corner_radius=6, border_width=1, border_color="#E5E7EB")
                pbox.pack(fill="x", padx=14, pady=(2, 6))
                
                plbl = ctk.CTkLabel(
                    pbox,
                    text=f"📁 {path_val}",
                    font=("Consolas" if os.name == "nt" else FONT_FAMILY, 11, "bold"),
                    text_color="#1F2937",
                    anchor="w",
                )
                plbl.pack(side="left", padx=10, pady=6, fill="x", expand=True)

                def make_copy_path_cmd(val: str):
                    return lambda: self._copy_text(val, "Path copied!")

                btn_cpath = ctk.CTkButton(
                    pbox,
                    text="Copy",
                    width=54,
                    height=24,
                    font=(FONT_FAMILY, 10),
                    fg_color="#E5E7EB",
                    hover_color="#D1D5DB",
                    text_color="#374151",
                    corner_radius=4,
                    command=make_copy_path_cmd(path_val),
                )
                btn_cpath.pack(side="right", padx=6, pady=4)

            # Bullet points
            bullets = card.get("bullets", [])
            for b in bullets:
                b_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
                b_frame.pack(fill="x", padx=16, pady=1)

                dot = ctk.CTkLabel(
                    b_frame,
                    text="•",
                    font=(FONT_FAMILY, 13, "bold"),
                    text_color="#D81B60",
                    width=12,
                )
                dot.pack(side="left", anchor="n")

                b_lbl = ctk.CTkLabel(
                    b_frame,
                    text=b,
                    font=(FONT_FAMILY, 11),
                    text_color="#374151",
                    justify="left",
                    anchor="w",
                    wraplength=630,
                )
                b_lbl.pack(side="left", fill="x", expand=True, padx=(4, 0))

            # Special Credit Box for Community
            if card.get("credit_box"):
                cbox = ctk.CTkFrame(card_frame, fg_color="#FAF5FF", corner_radius=8, border_width=1, border_color="#E9D5FF")
                cbox.pack(fill="x", padx=14, pady=(8, 10))

                cbox_title = ctk.CTkLabel(
                    cbox,
                    text="🔗 Official Discord Invite & Credits",
                    font=(FONT_FAMILY, 12, "bold"),
                    text_color="#7E22CE",
                    anchor="w",
                )
                cbox_title.pack(fill="x", padx=12, pady=(8, 4))

                credit_text_lbl = ctk.CTkLabel(
                    cbox,
                    text=f"⭐ {DISCORD_CREDIT_FULL}",
                    font=(FONT_FAMILY, 12, "bold"),
                    text_color="#9C27B0",
                    anchor="w",
                )
                credit_text_lbl.pack(fill="x", padx=14, pady=(0, 6))

                action_row = ctk.CTkFrame(cbox, fg_color="transparent")
                action_row.pack(fill="x", padx=12, pady=(0, 8))

                btn_discord_act = ctk.CTkButton(
                    action_row,
                    text=f"💬 {t('guide_btn_join_discord')} ({DISCORD_INVITE_SHORT})",
                    font=(FONT_FAMILY, 11, "bold"),
                    fg_color=COLOR_DISCORD,
                    hover_color="#7B1FA2",
                    text_color="white",
                    height=32,
                    corner_radius=UI_RADIUS,
                    command=self.open_discord,
                )
                btn_discord_act.pack(side="left", padx=(0, 8))

                btn_copy_act = ctk.CTkButton(
                    action_row,
                    text=f"📋 {t('guide_btn_copy_link')}",
                    font=(FONT_FAMILY, 11),
                    fg_color="#FFFFFF",
                    hover_color="#F3E8FF",
                    text_color="#581C87",
                    border_width=1,
                    border_color="#D8B4FE",
                    height=32,
                    corner_radius=UI_RADIUS,
                    command=self.copy_discord_link,
                )
                btn_copy_act.pack(side="left")

            # Standalone action button if specified
            act_type = card.get("action_type")
            act_text = card.get("action_text")
            if act_type and act_text:
                btn_act_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
                btn_act_frame.pack(fill="x", padx=14, pady=(6, 10))

                if act_type == "select_folder":
                    def on_select_click():
                        if hasattr(self.app, "select_log_folder"):
                            self.app.select_log_folder()
                    btn_standalone = ctk.CTkButton(
                        btn_act_frame,
                        text=act_text,
                        font=(FONT_FAMILY, 11, "bold"),
                        fg_color="#0284C7",
                        hover_color="#0369A1",
                        text_color="white",
                        height=30,
                        corner_radius=UI_RADIUS,
                        command=on_select_click,
                    )
                    btn_standalone.pack(side="left")
                elif act_type == "open_web_war":
                    btn_standalone = ctk.CTkButton(
                        btn_act_frame,
                        text=act_text,
                        font=(FONT_FAMILY, 11, "bold"),
                        fg_color="#0284C7",
                        hover_color="#0369A1",
                        text_color="white",
                        height=30,
                        corner_radius=UI_RADIUS,
                        command=lambda: webbrowser.open(DEFAULT_WAR_ROOM_URL),
                    )
                    btn_standalone.pack(side="left")

            card_frame.pack_configure(pady=(4, 8))

    def open_discord(self) -> None:
        """Open official Discord invite URL."""
        try:
            webbrowser.open(DEFAULT_DISCORD_URL)
        except Exception:
            pass

    def copy_discord_link(self) -> None:
        """Copy Discord invite link to system clipboard and show toast."""
        self._copy_text(DEFAULT_DISCORD_URL, t("guide_link_copied"))

    def _copy_text(self, text_to_copy: str, feedback_msg: str) -> None:
        try:
            self.clipboard_clear()
            self.clipboard_append(text_to_copy)
            self.update()
            self.show_toast(feedback_msg)
        except Exception:
            pass

    def show_toast(self, message: str) -> None:
        self.lbl_toast.configure(text=message)
        self.after(2800, lambda: self.lbl_toast.configure(text=""))


def open_guide_dialog(parent: Any, initial_tab: str = "setup") -> GuideWindow:
    """
    Open or bring to front the single-instance 3-Language Guide Window.
    """
    existing = getattr(parent, "guide_window", None)
    if existing and existing.winfo_exists():
        existing.lift()
        existing.focus_force()
        if initial_tab != existing.current_tab:
            existing.current_tab = initial_tab
            init_label = existing.tab_map.get(initial_tab, existing.tab_labels[0])
            existing.seg_tabs.set(init_label)
            existing.render_tab_content(initial_tab)
        return existing

    guide = GuideWindow(parent, initial_tab=initial_tab)
    parent.guide_window = guide
    return guide
