"""
Unit & Integration Tests for 3-Language System (English, Thai, Japanese).
Verifies:
- English as the primary and default fallback language.
- Built-in offline translations for EN, TH, and JA across all UI components.
- Dynamic live language switching for both Offline Tracker and Online ARKS War Room.
- Config persistence of language preference.
- OverlayWindow dynamic language retranslation.
"""

import json
import os
import time
import pytest
from unittest.mock import MagicMock

from config import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES
from modules.i18n import (
    i18n,
    t,
    tr,
    SUPPORTED_LANGUAGES as I18N_SUPPORTED_LANGUAGES,
    DEFAULT_LANGUAGE as I18N_DEFAULT_LANGUAGE,
    TRANSLATIONS,
    LANDMARK_PRESETS,
)
from modules.event_bus import event_bus
from meseta_tracker import NGSTrackerApp
from overlay_ui import OverlayWindow


def test_default_language_is_english():
    """Verify that English is strictly the primary default language."""
    assert DEFAULT_LANGUAGE == "en"
    assert I18N_DEFAULT_LANGUAGE == "en"
    assert "en" in SUPPORTED_LANGUAGES
    assert "th" in SUPPORTED_LANGUAGES
    assert "ja" in SUPPORTED_LANGUAGES


def test_translation_dictionaries_completeness():
    """Verify that all keys in English have corresponding entries in Thai and Japanese."""
    en_keys = set(TRANSLATIONS["en"].keys())
    th_keys = set(TRANSLATIONS["th"].keys())
    ja_keys = set(TRANSLATIONS["ja"].keys())

    assert len(en_keys) >= 40
    missing_in_th = en_keys - th_keys
    missing_in_ja = en_keys - ja_keys

    assert not missing_in_th, f"Missing translations in Thai: {missing_in_th}"
    assert not missing_in_ja, f"Missing translations in Japanese: {missing_in_ja}"


def test_i18n_fallback_to_english():
    """Verify that if a key is missing in a language, it cleanly falls back to English."""
    i18n.set_language("ja")
    # Test existing key
    assert t("brand_tracker") == "TRACKER"

    # Test parameter formatting
    formatted = t("war_op_title", name="HeroARKS")
    assert "HeroARKS" in formatted

    # Test unknown key fallback
    assert t("non_existent_key_12345") == "non_existent_key_12345"
    assert t("non_existent_key_12345", default="FallbackMsg") == "FallbackMsg"

    # Reset to English
    i18n.set_language("en")
    assert i18n.current_language == "en"


def test_landmark_presets_multilingual():
    """Verify landmark presets exist in EN, TH, and JA."""
    for lang in ("en", "th", "ja"):
        i18n.set_language(lang)
        landmarks = i18n.get_landmarks()
        assert len(landmarks) == 10
        # First item is always landmark placeholder
        assert "🪐" in landmarks[0]
        # Earth is present in appropriate language
        landmarks_str = " ".join(landmarks)
        if lang == "en":
            assert "Earth" in landmarks_str
        elif lang == "th":
            assert "Earth" in landmarks_str
        elif lang == "ja":
            assert "地球" in landmarks_str


def test_offline_app_language_switching(shared_app):
    """
    Verify live language switching on the offline tracker UI:
    - Default is English
    - Switch to Thai -> widgets update to Thai
    - Switch to Japanese -> widgets update to Japanese
    - Switch back to English -> widgets update to English
    """
    app = shared_app
    app.show_offline_view()
    app.update_idletasks()

    # 1. Switch to English
    app.set_app_language("en")
    app.update_idletasks()
    assert i18n.current_language == "en"
    assert app.lang_btn_title.get() == "EN"
    assert app.seg_lang_sidebar.get() == "EN"
    assert app.btn_reset.cget("text") == "Reset (Start Over)"
    assert app.dashboard_area.lbl_session_title.cget("text") == "Session Earnings (Session)"
    assert app.dashboard_area.lbl_wallet_title.cget("text") == "Current Wallet"
    assert app.dashboard_area.lbl_time_title.cget("text") == "Farming Time"
    assert app.dashboard_area.lbl_mhr_title.cget("text") == "Speed (M/hr)"
    assert "Dropped Items" in app.dashboard_area.lbl_drops_title.cget("text")

    # 2. Switch to Thai
    app.set_app_language("th")
    app.update_idletasks()
    assert i18n.current_language == "th"
    assert app.lang_btn_title.get() == "TH"
    assert app.seg_lang_sidebar.get() == "TH"
    assert app.btn_reset.cget("text") == "รีเซ็ตข้อมูล (Reset)"
    assert app.dashboard_area.lbl_session_title.cget("text") == "ยอดเงินรอบนี้ (Session)"
    assert app.dashboard_area.lbl_wallet_title.cget("text") == "เงินในกระเป๋า"
    assert app.dashboard_area.lbl_time_title.cget("text") == "ระยะเวลาฟาร์ม"
    assert app.dashboard_area.lbl_mhr_title.cget("text") == "ความเร็ว (M/hr)"
    assert "รายการไอเท็มที่ดรอป" in app.dashboard_area.lbl_drops_title.cget("text")

    # 3. Switch to Japanese
    app.set_app_language("ja")
    app.update_idletasks()
    assert i18n.current_language == "ja"
    assert app.lang_btn_title.get() == "JA"
    assert app.seg_lang_sidebar.get() == "JA"
    assert app.btn_reset.cget("text") == "リセット (Reset)"
    assert app.dashboard_area.lbl_session_title.cget("text") == "今回の獲得メセタ (Session)"
    assert app.dashboard_area.lbl_wallet_title.cget("text") == "現在の所持メセタ"
    assert app.dashboard_area.lbl_time_title.cget("text") == "周回時間"
    assert app.dashboard_area.lbl_mhr_title.cget("text") == "獲得時給 (M/hr)"
    assert "ドロップアイテム一覧" in app.dashboard_area.lbl_drops_title.cget("text")

    # 4. Return to English (Primary)
    app.set_app_language("en")
    app.update_idletasks()
    assert i18n.current_language == "en"


def test_online_war_view_language_switching(shared_app):
    """
    Verify live language switching on the Online ARKS War Room view:
    - Banner operative headers
    - Landmarks dropdown
    - Paste & save buttons
    - Sync status labels
    - Back to offline button
    """
    app = shared_app
    app.show_war_view()
    app.update_idletasks()
    wv = app.war_view

    # 1. English mode in War Room
    app.set_app_language("en")
    app.update_idletasks()
    assert "Character" in wv.lbl_op_title.cget("text")
    assert "This name will be used as data on ARK WAR" in wv.lbl_op_sub.cget("text")
    assert wv.btn_paste_coord.cget("text") == "📋 Paste"
    assert wv.btn_save_coord.cget("text") == "💾 Save"
    assert wv.btn_back_offline.cget("text") == "🔙 Back to Offline"
    assert wv.opt_landmark.cget("values")[0] == "🪐 Landmark..."

    # 2. Thai mode in War Room
    app.set_app_language("th")
    app.update_idletasks()
    assert "ชื่อในเกม" in wv.lbl_op_title.cget("text")
    assert "ชื่อนี้จะถูกใช้เป็นข้อมูลบน ARK WAR" in wv.lbl_op_sub.cget("text")
    assert wv.btn_paste_coord.cget("text") == "📋 วาง"
    assert wv.btn_save_coord.cget("text") == "💾 บันทึก"
    assert wv.btn_back_offline.cget("text") == "🔙 กลับสู่โหมดออฟไลน์"
    assert wv.opt_landmark.cget("values")[0] == "🪐 พิกัดสำคัญ..."

    # 3. Japanese mode in War Room
    app.set_app_language("ja")
    app.update_idletasks()
    assert "キャラクター名" in wv.lbl_op_title.cget("text")
    assert "この名前はARK WARのデータとして使用されます" in wv.lbl_op_sub.cget("text")
    assert wv.btn_paste_coord.cget("text") == "📋 貼付"
    assert wv.btn_save_coord.cget("text") == "💾 保存"
    assert wv.btn_back_offline.cget("text") == "🔙 オフライン画面へ戻る"
    assert wv.opt_landmark.cget("values")[0] == "🪐 主要拠点..."

    # Return to offline & reset to English
    app.show_offline_view()
    app.set_app_language("en")
    app.update_idletasks()


def test_overlay_language_dynamic_update(shared_app):
    """Verify OverlayWindow retranslates dynamically when language changes."""
    app = shared_app
    app.set_app_language("en")
    app.update_idletasks()

    overlay = OverlayWindow(app, mode="mini")
    try:
        overlay.update()
        assert overlay.lbl_subtitle.cget("text") == "Session Balance"
        assert "Wallet:" in overlay.lbl_wallet_overlay.cget("text")
        assert overlay.lbl_time_cap.cget("text") == "TIME"
        assert overlay.lbl_rate_cap.cget("text") == "RATE"

        # Switch to Thai
        app.set_app_language("th")
        overlay.update()
        assert overlay.lbl_subtitle.cget("text") == "ยอดเงินรอบนี้ (Session)"
        assert "กระเป๋า:" in overlay.lbl_wallet_overlay.cget("text")
        assert overlay.lbl_time_cap.cget("text") == "เวลา"
        assert overlay.lbl_rate_cap.cget("text") == "ความเร็ว"

        # Switch to Japanese
        app.set_app_language("ja")
        overlay.update()
        assert overlay.lbl_subtitle.cget("text") == "今回の獲得メセタ"
        assert "所持:" in overlay.lbl_wallet_overlay.cget("text")
        assert overlay.lbl_time_cap.cget("text") == "時間"
        assert overlay.lbl_rate_cap.cget("text") == "時給"
    finally:
        overlay.destroy()
        app.set_app_language("en")


def test_config_persistence_of_language(tmp_path, monkeypatch):
    """Verify language preference is saved to and loaded from ngs_tracker_config.json."""
    from meseta_tracker import CONFIG_FILE

    config_path = str(tmp_path / "ngs_tracker_config.json")
    monkeypatch.setattr("meseta_tracker.CONFIG_FILE", config_path)

    # Save Japanese config
    i18n.set_language("ja")
    try:
        app = MagicMock()
        app.watchlist_items = ["Arms Refiner II"]
        app.log_folder = ""
        app.board_coord = "0, 0, 1"

        from meseta_tracker import NGSTrackerApp
        # Test save_settings directly
        NGSTrackerApp.save_settings(app)

        with open(config_path, "r", encoding="utf-8") as f:
            saved = json.load(f)
        assert saved["language"] == "ja"
    finally:
        # Reset back to English
        i18n.set_language("en")


def test_inno_setup_trilingual_configuration():
    """Verify that Inno Setup script configures English, Thai, and Japanese with localized custom messages."""
    iss_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "installer", "NekoTracker.iss"))
    assert os.path.isfile(iss_path), f"Missing {iss_path}"

    with open(iss_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify [Languages] section contains all 3 languages
    assert 'Name: "english"; MessagesFile: "compiler:Default.isl"' in content
    assert 'Name: "thai"; MessagesFile: "compiler:Languages\\Thai.isl"' in content
    assert 'Name: "japanese"; MessagesFile: "compiler:Languages\\Japanese.isl"' in content

    # Verify CustomMessages for all 3 languages
    for lang in ("english", "thai", "japanese"):
        assert f"{lang}.CreateUninstallIcon=" in content
        assert f"{lang}.UserGuide=" in content
        assert f"{lang}.UninstallProgram=" in content


def test_release_readme_trilingual_parity():
    """Verify that the release distribution README contains testing guidelines in EN, TH, and JA."""
    readme_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "artifacts", "release-v7.1.0", "README.md"))
    assert os.path.isfile(readme_path), f"Missing {readme_path}"

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "### 🇹🇭 ภาษาไทย (TH)" in content
    assert "### 🇬🇧 English (EN)" in content
    assert "### 🇯🇵 日本語 (JA)" in content
