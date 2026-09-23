"""
Internationalization (i18n) Module for NEKO Item & Meseta Tracker.
Supports 3 languages: English (en, Primary/Default), Thai (th), and Japanese (ja).
Provides offline built-in translation catalogs and event-driven language updates
for both Offline Tracking and Online ARKS War Room features.
"""

from __future__ import annotations

import locale
from typing import Any, Callable, Dict, List, Optional

SUPPORTED_LANGUAGES = ["en", "th", "ja"]
DEFAULT_LANGUAGE = "en"

LANGUAGE_DISPLAY_NAMES: Dict[str, str] = {
    "en": "English",
    "th": "ไทย",
    "ja": "日本語",
}

LANGUAGE_BUTTON_LABELS: Dict[str, str] = {
    "en": "EN",
    "th": "TH",
    "ja": "JA",
}

LANGUAGE_CODE_MAP: Dict[str, str] = {
    "en": "en",
    "english": "en",
    "th": "th",
    "thai": "th",
    "ja": "ja",
    "jp": "ja",
    "japanese": "ja",
    "日本語": "ja",
    "ไทย": "th",
}

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # App & Window Titles
        "app_window_title": "NEKO Item & Meseta Tracker",
        "app_title_offline": "NEKO FAMILY TEAM SHOP - Item & Meseta tracker",
        "app_title_war": "NEKO FAMILY — ARKS War Room Realtime Meseta Tracker",
        "brand_subtitle": "ITEM & MESETA",
        "brand_tracker": "TRACKER",
        "brand_created_by": "CREATED BY",
        "brand_team_credit": "TEAM NEKO FAMILY SHIP 4 TH",

        # Sidebar Buttons & Toggles
        "btn_enter_war": "⚔️ Enter War (ARKS War)",
        "btn_enter_war_char": "⚔️ Enter War ({character})",
        "btn_reset": "Reset (Start Over)",
        "btn_watchlist": "Edit Watch List",
        "switch_filter": "Enable Watch List Filter",
        "btn_overlay_full": "Item & Meseta",
        "btn_overlay_mini": "Meseta",
        "btn_discord": "DISCORD NEKO FAMILY",
        "btn_uninstall": "Uninstall",
        "label_language": "Language",

        # Log Status & Folder Picker
        "status_no_folder": "Log folder not selected",
        "status_folder_unspecified": "Log folder not specified",
        "status_log_not_found": "No ActionLog file found",
        "status_reading_file": "Reading file: {file}",
        "btn_select_folder": "📂 Select Log Folder",

        # Dashboard Metric Cards
        "lbl_session": "Session Earnings (Session)",
        "lbl_wallet": "Current Wallet",
        "lbl_farming_time": "Farming Time",
        "lbl_speed": "Speed (M/hr)",
        "header_drops": "📦 Dropped Items",
        "search_placeholder": "🔍 Search items...",

        # Drop List Empty States
        "empty_waiting": "Waiting for drops...",
        "empty_not_found": "Not found: {keyword}",
        "empty_watchlist_no_match": "No items match Watch List",
        "empty_watchlist_empty": "Watch List is empty",

        # Reset Confirmation Dialog
        "dialog_reset_title": "Confirm Reset",
        "dialog_reset_msg": "Reset this session's data?\nAll earnings, duration, and drops will be cleared.",
        "btn_cancel": "Cancel",
        "btn_confirm_reset": "Confirm Reset",

        # Watch List Editor Dialog
        "dialog_watchlist_title": "Watch List Editor",
        "dialog_watchlist_prompt": "Enter item names to focus on (1 per line)",
        "btn_save_watchlist": "Save (Save Config)",

        # Overlay Window
        "overlay_window_title": "Gadget Mode - NEKO Tracker",
        "overlay_title_full": "ITEM • MESETA",
        "overlay_title_mini": "MESETA",
        "overlay_subtitle": "Session Balance",
        "overlay_wallet": "Wallet: {wallet}",
        "overlay_time_cap": "TIME",
        "overlay_rate_cap": "RATE",
        "overlay_drops_cap": "DROPS",
        "overlay_focus_badge": "● FOCUS",
        "overlay_waiting": "Waiting for drops…",
        "overlay_focus_empty": "🔎 Focus Mode",

        # War Mode (Online)
        "war_op_title": "👤 Character: {name}",
        "war_op_sub": "This name will be used as data on ARK WAR",
        "war_coord_label": "🎯 Coord [X, Y]:",
        "war_paste_btn": "📋 Paste",
        "war_pasted_btn": "✓ Pasted",
        "war_save_btn": "💾 Save",
        "war_landmark_default": "🪐 Landmark...",
        "war_sync_ready": "⚡ Auto-sync ready",
        "war_sync_btn": "⚡ Sync Now",
        "war_syncing": "⚡ Syncing live data...",
        "war_synced": "⚡ Cloud Synced: {time} (+{contrib} ℳ)",
        "war_sync_waiting": "⚡ Waiting for connection...",
        "war_sync_error": "⚡ Failed to sync telemetry",
        "war_btn_open_web": "🪐 ARKS War Room (Web)",
        "war_btn_back_offline": "🔙 Back to Offline",

        # War Mode Context Menu
        "menu_cut": "✂️ Cut",
        "menu_copy": "📄 Copy",
        "menu_paste_coord": "📋 Paste Coord",
        "menu_select_all": "🔘 Select All",

        # Security & Service Messages
        "msg_anti_tamper_compromised": "Data tampering detected (Anti-Tamper Compromised): Cloud sync suspended",
        "msg_security_revoked": "Client version ({version}) revoked for security: Cloud sync rejected",

        # Guide / How-To-Use & Community
        "btn_how_to_use": "📖 How to Use",
        "dialog_guide_title": "How to Use — NEKO Item & Meseta Tracker",
        "guide_tab_setup": "🚀 Setup & Logs",
        "guide_tab_tracking": "💰 Meseta & Items",
        "guide_tab_overlay": "🪟 Gadget Overlay",
        "guide_tab_war": "⚔️ ARKS War",
        "guide_tab_community": "🌸 Community & Credit",
        "guide_btn_join_discord": "💬 Join Discord Community",
        "guide_btn_copy_link": "📋 Copy Discord Link",
        "guide_link_copied": "✓ Copied to Clipboard!",
        "guide_credit_label": "NEKO★FAMILY PSO2:NGS Community discord.gg/fkjXW9AJ6a",
        "guide_community_desc": "Official PSO2:NGS gaming community for team members and players. Join us for farming runs, strategies, tracker updates, and ARKS War Room campaigns!",
        "guide_close_btn": "✕ Close Guide",
    },
    "th": {
        # App & Window Titles
        "app_window_title": "NEKO ติดตามไอเท็ม & เมเซต้า",
        "app_title_offline": "NEKO FAMILY TEAM SHOP - Item & Meseta tracker",
        "app_title_war": "NEKO FAMILY — ARKS War Room Realtime Meseta Tracker",
        "brand_subtitle": "ITEM & MESETA",
        "brand_tracker": "TRACKER",
        "brand_created_by": "CREATED BY",
        "brand_team_credit": "TEAM NEKO FAMILY SHIP 4 TH",

        # Sidebar Buttons & Toggles
        "btn_enter_war": "⚔️ เข้าร่วมสงคราม (ARKS War)",
        "btn_enter_war_char": "⚔️ เข้าร่วมสงคราม ({character})",
        "btn_reset": "รีเซ็ตข้อมูล (Reset)",
        "btn_watchlist": "แก้ไข Watch List",
        "switch_filter": "กรองเฉพาะ Watch List",
        "btn_overlay_full": "Item & Meseta",
        "btn_overlay_mini": "Meseta",
        "btn_discord": "DISCORD NEKO FAMILY",
        "btn_uninstall": "ถอนการติดตั้ง",
        "label_language": "ภาษา",

        # Log Status & Folder Picker
        "status_no_folder": "ยังไม่ได้เลือกโฟลเดอร์ Log",
        "status_folder_unspecified": "ยังไม่ได้ระบุโฟลเดอร์ Log",
        "status_log_not_found": "ไม่พบไฟล์ Log",
        "status_reading_file": "กำลังอ่านไฟล์: {file}",
        "btn_select_folder": "📂 เลือกโฟลเดอร์ Log",

        # Dashboard Metric Cards
        "lbl_session": "ยอดเงินรอบนี้ (Session)",
        "lbl_wallet": "เงินในกระเป๋า",
        "lbl_farming_time": "ระยะเวลาฟาร์ม",
        "lbl_speed": "ความเร็ว (M/hr)",
        "header_drops": "📦 รายการไอเท็มที่ดรอป",
        "search_placeholder": "🔍 ค้นหาไอเท็ม...",

        # Drop List Empty States
        "empty_waiting": "รอไอเท็มดรอป...",
        "empty_not_found": "ไม่พบ: '{keyword}'",
        "empty_watchlist_no_match": "ไม่พบไอเท็มใน Watch List",
        "empty_watchlist_empty": "ไม่มีรายการใน Watch List",

        # Reset Confirmation Dialog
        "dialog_reset_title": "ยืนยันการรีเซ็ต",
        "dialog_reset_msg": "ต้องการรีเซ็ตข้อมูลรอบนี้หรือไม่?\n(ยอดเงิน เวลา และไอเท็มทั้งหมดจะถูกล้างค่า)",
        "btn_cancel": "ยกเลิก",
        "btn_confirm_reset": "ยืนยันรีเซ็ต",

        # Watch List Editor Dialog
        "dialog_watchlist_title": "แก้ไข Watch List",
        "dialog_watchlist_prompt": "ระบุชื่อไอเท็มที่ต้องการเฝ้าระวัง (บรรทัดละ 1 ชื่อ)",
        "btn_save_watchlist": "บันทึกข้อมูล",

        # Overlay Window
        "overlay_window_title": "โหมดหน้าต่างย่อ (Overlay) - NEKO Tracker",
        "overlay_title_full": "ITEM • MESETA",
        "overlay_title_mini": "MESETA",
        "overlay_subtitle": "ยอดเงินรอบนี้ (Session)",
        "overlay_wallet": "กระเป๋า: {wallet}",
        "overlay_time_cap": "เวลา",
        "overlay_rate_cap": "ความเร็ว",
        "overlay_drops_cap": "ดรอป",
        "overlay_focus_badge": "● โฟกัส",
        "overlay_waiting": "รอไอเท็มดรอป…",
        "overlay_focus_empty": "🔎 โหมดโฟกัส",

        # War Mode (Online)
        "war_op_title": "👤 ชื่อในเกม: {name}",
        "war_op_sub": "ชื่อนี้จะถูกใช้เป็นข้อมูลบน ARK WAR",
        "war_coord_label": "🎯 พิกัด [X, Y]:",
        "war_paste_btn": "📋 วาง",
        "war_pasted_btn": "✓ วางแล้ว",
        "war_save_btn": "💾 บันทึก",
        "war_landmark_default": "🪐 พิกัดเป้าหมาย...",
        "war_sync_ready": "⚡ ระบบซิงค์อัตโนมัติพร้อมทำงาน",
        "war_sync_btn": "⚡ ซิงค์ข้อมูล",
        "war_syncing": "⚡ กำลังซิงค์ข้อมูลออนไลน์...",
        "war_synced": "⚡ ซิงค์ข้อมูลล่าสุด: {time} (+{contrib} ℳ)",
        "war_sync_waiting": "⚡ กำลังรอการเชื่อมต่อ...",
        "war_sync_error": "⚡ ส่งข้อมูลไม่สำเร็จ (เชื่อมต่อล้มเหลว)",
        "war_btn_open_web": "🪐 ARKS War Room (Web)",
        "war_btn_back_offline": "🔙 กลับสู่โหมดออฟไลน์",

        # War Mode Context Menu
        "menu_cut": "✂️ ตัด (Cut)",
        "menu_copy": "📄 คัดลอก (Copy)",
        "menu_paste_coord": "📋 วางพิกัด (Paste)",
        "menu_select_all": "🔘 เลือกทั้งหมด",

        # Security & Service Messages
        "msg_anti_tamper_compromised": "⚠️ ตรวจพบการดัดแปลงข้อมูล (Anti-Tamper Compromised): ระงับการส่งข้อมูลสถิติ",
        "msg_security_revoked": "⚠️ เวอร์ชันไคลเอนต์ ({version}) ไม่ผ่านเกณฑ์ความปลอดภัย: ระงับการส่งข้อมูล",

        # Guide / How-To-Use & Community
        "btn_how_to_use": "📖 วิธีใช้งาน",
        "dialog_guide_title": "วิธีใช้งาน — NEKO Item & Meseta Tracker",
        "guide_tab_setup": "🚀 เริ่มต้น & Log",
        "guide_tab_tracking": "💰 เมเซต้า & ไอเท็ม",
        "guide_tab_overlay": "🪟 โหมดหน้าต่างย่อ (Overlay)",
        "guide_tab_war": "⚔️ ARKS War",
        "guide_tab_community": "🌸 คอมมูนิตี้",
        "guide_btn_join_discord": "💬 เข้าร่วม Discord คอมมูนิตี้",
        "guide_btn_copy_link": "📋 คัดลอกลิงก์ Discord",
        "guide_link_copied": "✓ คัดลอกลิงก์เรียบร้อยแล้ว!",
        "guide_credit_label": "NEKO★FAMILY PSO2:NGS Community discord.gg/fkjXW9AJ6a",
        "guide_community_desc": "คอมมูนิตี้สำหรับผู้เล่น PSO2:NGS ร่วมพูดคุย แลกเปลี่ยนเทคนิคฟาร์ม แจ้งปัญหา และลุยกิจกรรม ARKS War Room ไปด้วยกัน!",
        "guide_close_btn": "✕ ปิดหน้าต่างคู่มือ",
    },
    "ja": {
        # App & Window Titles
        "app_window_title": "NEKO アイテム＆メセタトラッカー",
        "app_title_offline": "NEKO FAMILY TEAM SHOP - アイテム＆メセタトラッカー",
        "app_title_war": "NEKO FAMILY — ARKS War Room リアルタイムメセタトラッカー",
        "brand_subtitle": "ITEM & MESETA",
        "brand_tracker": "TRACKER",
        "brand_created_by": "CREATED BY",
        "brand_team_credit": "TEAM NEKO FAMILY SHIP 4 TH",

        # Sidebar Buttons & Toggles
        "btn_enter_war": "⚔️ 作戦参加 (ARKS War)",
        "btn_enter_war_char": "⚔️ 作戦参加 ({character})",
        "btn_reset": "リセット (Reset)",
        "btn_watchlist": "ウォッチリスト編集",
        "switch_filter": "ウォッチリストフィルター有効",
        "btn_overlay_full": "Item & Meseta",
        "btn_overlay_mini": "Meseta",
        "btn_discord": "DISCORD NEKO FAMILY",
        "btn_uninstall": "アンインストール",
        "label_language": "言語",

        # Log Status & Folder Picker
        "status_no_folder": "ログフォルダ未選択",
        "status_folder_unspecified": "ログフォルダが指定されていません",
        "status_log_not_found": "ログファイルが見つかりません",
        "status_reading_file": "ログ読込中: {file}",
        "btn_select_folder": "📂 ログフォルダを選択",

        # Dashboard Metric Cards
        "lbl_session": "今回の獲得メセタ (Session)",
        "lbl_wallet": "現在の所持メセタ",
        "lbl_farming_time": "周回時間",
        "lbl_speed": "獲得時給 (M/hr)",
        "header_drops": "📦 ドロップアイテム一覧",
        "search_placeholder": "🔍 アイテム検索...",

        # Drop List Empty States
        "empty_waiting": "ドロップ待機中...",
        "empty_not_found": "見つかりません: {keyword}",
        "empty_watchlist_no_match": "ウォッチリストのアイテムなし",
        "empty_watchlist_empty": "ウォッチリストが空です",

        # Reset Confirmation Dialog
        "dialog_reset_title": "リセット確認",
        "dialog_reset_msg": "今回のセッションデータをリセットしますか？\n獲得メセタ、周回時間、ドロップ記録がすべて初期化されます。",
        "btn_cancel": "キャンセル",
        "btn_confirm_reset": "リセット実行",

        # Watch List Editor Dialog
        "dialog_watchlist_title": "ウォッチリスト編集",
        "dialog_watchlist_prompt": "注目するアイテム名を入力（1行に1つ）",
        "btn_save_watchlist": "設定を保存 (Save)",

        # Overlay Window
        "overlay_window_title": "ガジェットモード - NEKO Tracker",
        "overlay_title_full": "ITEM • MESETA",
        "overlay_title_mini": "MESETA",
        "overlay_subtitle": "今回の獲得メセタ",
        "overlay_wallet": "所持: {wallet}",
        "overlay_time_cap": "時間",
        "overlay_rate_cap": "時給",
        "overlay_drops_cap": "ドロップ",
        "overlay_focus_badge": "● 注目",
        "overlay_waiting": "ドロップ待機中…",
        "overlay_focus_empty": "🔎 フォーカス中",

        # War Mode (Online)
        "war_op_title": "👤 キャラクター名: {name}",
        "war_op_sub": "この名前はARK WARのデータとして使用されます",
        "war_coord_label": "🎯 作戦座標 [X, Y]:",
        "war_paste_btn": "📋 貼付",
        "war_pasted_btn": "✓ 貼付済",
        "war_save_btn": "💾 保存",
        "war_landmark_default": "🪐 主要拠点...",
        "war_sync_ready": "⚡ 自動同期待機中",
        "war_sync_btn": "⚡ 今すぐ同期",
        "war_syncing": "⚡ クラウド同期中...",
        "war_synced": "⚡ クラウド同期完了: {time} (+{contrib} ℳ)",
        "war_sync_waiting": "⚡ 接続待機中...",
        "war_sync_error": "⚡ テレメトリ同期に失敗しました",
        "war_btn_open_web": "🪐 ARKS War Room (Web)",
        "war_btn_back_offline": "🔙 オフライン画面へ戻る",

        # War Mode Context Menu
        "menu_cut": "✂️ 切り取り (Cut)",
        "menu_copy": "📄 コピー (Copy)",
        "menu_paste_coord": "📋 座標を貼り付け (Paste)",
        "menu_select_all": "🔘 すべて選択 (Select All)",

        # Security & Service Messages
        "msg_anti_tamper_compromised": "不正改ざん検知 (Anti-Tamper): クラウド同期を停止しました",
        "msg_security_revoked": "クライアントバージョン ({version}) はセキュリティ失効対象です: 同期を拒否しました",

        # Guide / How-To-Use & Community
        "btn_how_to_use": "📖 使い方ガイド",
        "dialog_guide_title": "使い方ガイド — NEKO アイテム＆メセタトラッカー",
        "guide_tab_setup": "🚀 初期設定＆ログ",
        "guide_tab_tracking": "💰 メセタ＆アイテム",
        "guide_tab_overlay": "🪟 ガジェットオーバーレイ",
        "guide_tab_war": "⚔️ ARKS War 作戦",
        "guide_tab_community": "🌸 コミュニティ＆謝辞",
        "guide_btn_join_discord": "💬 Discordコミュニティに参加",
        "guide_btn_copy_link": "📋 Discordリンクをコピー",
        "guide_link_copied": "✓ クリップボードにコピーしました！",
        "guide_credit_label": "NEKO★FAMILY PSO2:NGS Community discord.gg/fkjXW9AJ6a",
        "guide_community_desc": "PSO2:NGS公式プレイヤーコミュニティ。周回攻略、アイテムドロップ情報、トラッカーの更新情報、ARKS War作戦への参加はこちら！",
        "guide_close_btn": "✕ ガイドを閉じる",
    },
}

LANDMARK_PRESETS: Dict[str, List[str]] = {
    "en": [
        "🪐 Landmark...",
        "🌌 Core [0, 0]",
        "🏙️ NGS [3, 3]",
        "🌍 Earth [9, -3]",
        "☀️ Sun [8, -3]",
        "🔴 Mars [9, -4]",
        "🌲 Naberius [-2, -2]",
        "🌋 Amduskia [-3, -3]",
        "🏜️ Lillipa [-1, -3]",
        "🚀 Hail Mary [20, 7]",
    ],
    "th": [
        "🪐 พิกัดสำคัญ...",
        "🌌 Core [0, 0]",
        "🏙️ NGS [3, 3]",
        "🌍 Earth [9, -3]",
        "☀️ Sun [8, -3]",
        "🔴 Mars [9, -4]",
        "🌲 Naberius [-2, -2]",
        "🌋 Amduskia [-3, -3]",
        "🏜️ Lillipa [-1, -3]",
        "🚀 Hail Mary [20, 7]",
    ],
    "ja": [
        "🪐 主要拠点...",
        "🌌 Core [0, 0]",
        "🏙️ NGS [3, 3]",
        "🌍 地球 [9, -3]",
        "☀️ 太陽 [8, -3]",
        "🔴 火星 [9, -4]",
        "🌲 ナベリウス [-2, -2]",
        "🌋 アムドゥスキア [-3, -3]",
        "🏜️ リリーパ [-1, -3]",
        "🚀 ヘイルメアリー [20, 7]",
    ],
}


class I18n:
    """
    Thread-safe localization manager.
    Defaults to English ('en') as the primary language.
    """

    def __init__(self, default_lang: str = DEFAULT_LANGUAGE) -> None:
        self._current_lang = DEFAULT_LANGUAGE
        self._listeners: List[Callable[[str], None]] = []
        self.set_language(default_lang, notify=False)

    @property
    def current_language(self) -> str:
        return self._current_lang

    def get_language(self) -> str:
        return self._current_lang

    def normalize_lang_code(self, lang: Optional[str]) -> str:
        if not lang:
            return DEFAULT_LANGUAGE
        cleaned = str(lang).strip().lower()
        return LANGUAGE_CODE_MAP.get(cleaned, DEFAULT_LANGUAGE)

    def set_language(self, lang: str, notify: bool = True) -> bool:
        normalized = self.normalize_lang_code(lang)
        changed = normalized != self._current_lang
        self._current_lang = normalized

        if changed and notify:
            try:
                from modules.event_bus import event_bus
                event_bus.emit("language_changed", language=self._current_lang)
            except Exception:
                pass

            for callback in list(self._listeners):
                try:
                    callback(self._current_lang)
                except Exception:
                    pass

        return changed

    def subscribe(self, callback: Callable[[str], None]) -> None:
        if callback not in self._listeners:
            self._listeners.append(callback)

    def unsubscribe(self, callback: Callable[[str], None]) -> None:
        if callback in self._listeners:
            self._listeners.remove(callback)

    def t(self, key: str, default: Optional[str] = None, **kwargs: Any) -> str:
        """
        Lookup translation for key.
        1. Try current language.
        2. Fallback to English ('en').
        3. Fallback to default or key.
        Format template variables using kwargs.
        """
        if not key:
            return ""

        cur_dict = TRANSLATIONS.get(self._current_lang, {})
        val = cur_dict.get(key)

        if val is None and self._current_lang != DEFAULT_LANGUAGE:
            en_dict = TRANSLATIONS.get(DEFAULT_LANGUAGE, {})
            val = en_dict.get(key)

        if val is None:
            val = default if default is not None else key

        if kwargs:
            try:
                return val.format(**kwargs)
            except Exception:
                return val
        return val

    def get_landmarks(self) -> List[str]:
        return LANDMARK_PRESETS.get(self._current_lang, LANDMARK_PRESETS[DEFAULT_LANGUAGE])

    def get_language_display_name(self, code: Optional[str] = None) -> str:
        code = self.normalize_lang_code(code or self._current_lang)
        return LANGUAGE_DISPLAY_NAMES.get(code, "English")

    def get_button_label(self, code: Optional[str] = None) -> str:
        code = self.normalize_lang_code(code or self._current_lang)
        return LANGUAGE_BUTTON_LABELS.get(code, "EN")


# Global singleton instance
i18n = I18n(DEFAULT_LANGUAGE)
t = i18n.t
tr = i18n.t
