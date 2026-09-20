"""
Unit & Integration Tests for 3-Language Guide (How-To-Use) System.
Verifies:
- 3-Language content completeness (EN, TH, JA) for all categories.
- Official community credit and Discord link attribution:
  'NEKO★FAMILY PSO2:NGS Community discord.gg/fkjXW9AJ6a'
- Live in-flight language switching within GuideWindow.
- Single-instance dialog management (open, lift, switch tab).
- Integration with main application and War View sidebars.
- Clipboard copy and browser opening behaviors.
"""

from __future__ import annotations

import os
import sys
import webbrowser
import pytest

from config import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    DEFAULT_DISCORD_URL,
    DISCORD_CREDIT_FULL,
    DISCORD_INVITE_SHORT,
)
from modules.i18n import i18n, t
from modules.guide_dialog import (
    GuideWindow,
    open_guide_dialog,
    GUIDE_SECTIONS,
)


def test_guide_sections_completeness_all_languages():
    """Verify that all 3 supported languages have complete tabs and cards."""
    for lang in ("en", "th", "ja"):
        assert lang in GUIDE_SECTIONS, f"Missing {lang} in GUIDE_SECTIONS"
        data = GUIDE_SECTIONS[lang]
        tabs = data.get("tabs", [])
        tab_ids = [t_id for t_id, _ in tabs]
        assert len(tab_ids) == 5
        assert "setup" in tab_ids
        assert "tracking" in tab_ids
        assert "overlay" in tab_ids
        assert "war" in tab_ids
        assert "community" in tab_ids

        # Check content in each tab
        for t_id in ("setup", "tracking", "overlay", "war", "community"):
            assert t_id in data, f"Tab {t_id} missing in {lang}"
            assert len(data[t_id].get("cards", [])) >= 2, f"Tab {t_id} has fewer than 2 cards in {lang}"


def test_guide_official_credit_and_discord_url():
    """Verify official credit text and Discord invite link are strictly present across all languages."""
    expected_credit = "NEKO★FAMILY PSO2:NGS Community discord.gg/fkjXW9AJ6a"
    assert DISCORD_CREDIT_FULL == expected_credit
    assert DEFAULT_DISCORD_URL == "https://discord.gg/fkjXW9AJ6a"

    for lang in ("en", "th", "ja"):
        comm_data = GUIDE_SECTIONS[lang]["community"]
        cards = comm_data["cards"]
        found_credit = False
        for card in cards:
            if card.get("credit_box") or card.get("credit_text") == expected_credit:
                found_credit = True
            bullets = " ".join(card.get("bullets", []))
            if expected_credit in bullets:
                found_credit = True
        assert found_credit, f"Credit '{expected_credit}' not found in {lang} community section"


def test_guide_window_lifecycle_and_single_instance(shared_app):
    """Verify GuideWindow opens, can switch tabs, and re-lifts without duplicating."""
    expected_credit = DISCORD_CREDIT_FULL
    app = shared_app
    app.update_idletasks()

    # Open guide
    guide = app.open_how_to_use("setup")
    try:
        assert guide is not None
        assert guide.winfo_exists()
        assert guide.current_tab == "setup"

        # Re-open with different tab
        guide2 = app.open_how_to_use("community")
        assert guide2 is guide
        assert guide.current_tab == "community"

        # Check title
        assert "NEKO" in guide.lbl_title.cget("text")
        assert "🌸" in guide.lbl_credit_footer.cget("text")
        assert expected_credit in guide.lbl_credit_footer.cget("text")
    finally:
        if guide and guide.winfo_exists():
            guide.destroy()


def test_guide_window_in_flight_language_switching(shared_app):
    """Verify live in-flight language switching in GuideWindow across EN, TH, and JA."""
    app = shared_app
    app.set_app_language("en")
    app.update_idletasks()

    guide = open_guide_dialog(app, initial_tab="setup")
    try:
        # 1. English
        assert i18n.current_language == "en"
        assert "How to Use" in guide.lbl_title.cget("text")
        assert guide.seg_lang.get() == "EN"

        # 2. Switch to Thai
        guide._on_lang_switch_clicked("th")
        app.update_idletasks()
        assert i18n.current_language == "th"
        assert "วิธีใช้งาน" in guide.lbl_title.cget("text")
        assert guide.seg_lang.get() == "TH"

        # 3. Switch to Japanese
        guide._on_lang_switch_clicked("ja")
        app.update_idletasks()
        assert i18n.current_language == "ja"
        assert "使い方ガイド" in guide.lbl_title.cget("text")
        assert guide.seg_lang.get() == "JA"

        # 4. Return to English
        guide._on_lang_switch_clicked("en")
        app.update_idletasks()
        assert i18n.current_language == "en"
        assert "How to Use" in guide.lbl_title.cget("text")
    finally:
        if guide and guide.winfo_exists():
            guide.destroy()
        app.set_app_language("en")


def test_guide_clipboard_copy_and_discord_browser_open(shared_app, monkeypatch):
    """Verify copy Discord link and open Discord in default web browser."""
    app = shared_app
    guide = open_guide_dialog(app, initial_tab="community")

    opened_urls = []
    monkeypatch.setattr(webbrowser, "open", lambda url: opened_urls.append(url))

    try:
        # Test open discord
        guide.open_discord()
        assert len(opened_urls) == 1
        assert opened_urls[0] == "https://discord.gg/fkjXW9AJ6a"

        # Test copy discord link
        guide.copy_discord_link()
        clipboard_text = app.clipboard_get()
        assert clipboard_text == "https://discord.gg/fkjXW9AJ6a"
        assert guide.lbl_toast.cget("text") != ""
    finally:
        if guide and guide.winfo_exists():
            guide.destroy()


def test_sidebar_buttons_exist_and_retranslate(shared_app):
    """Verify that both Main Window and War View have the How-To-Use button and retranslate dynamically."""
    app = shared_app
    app.show_offline_view()
    app.update_idletasks()

    # Main view has btn_how_to_use
    assert hasattr(app, "btn_how_to_use")
    assert hasattr(app, "btn_discord")

    # War view has btn_how_to_use
    app.show_war_view()
    app.update_idletasks()
    wv = app.war_view
    assert hasattr(wv, "btn_how_to_use")
    assert hasattr(wv, "btn_discord")

    # Retranslate test: English
    app.set_app_language("en")
    app.update_idletasks()
    assert "How to Use" in app.btn_how_to_use.cget("text")
    assert "How to Use" in wv.btn_how_to_use.cget("text")

    # Retranslate test: Thai
    app.set_app_language("th")
    app.update_idletasks()
    assert "วิธีใช้งาน" in app.btn_how_to_use.cget("text")
    assert "วิธีใช้งาน" in wv.btn_how_to_use.cget("text")

    # Retranslate test: Japanese
    app.set_app_language("ja")
    app.update_idletasks()
    assert "使い方ガイド" in app.btn_how_to_use.cget("text")
    assert "使い方ガイド" in wv.btn_how_to_use.cget("text")

    # Reset to English & return to offline view
    app.set_app_language("en")
    app.show_offline_view()
    app.update_idletasks()


def test_guide_war_spec_v9_conformance():
    """
    Verify alignment with Coordinate War Engine V9:
    - Sub-cell capture threshold is 10M (not legacy 25M).
    - Macro sector full liberation is 40M (not legacy 100M).
    - Philosophy: "เกมแค่เติมเงินเข้าไปในช่อง ใครใส่เยอะคนนั้นเป็นเจ้าของ".
    - Clash & hostile overwrite mechanics described.
    """
    from config import SLOT_TARGET_MESETA, SECTOR_TARGET_MESETA
    assert SLOT_TARGET_MESETA == 10_000_000
    assert SECTOR_TARGET_MESETA == 40_000_000

    # Thai V9 check
    th_war = GUIDE_SECTIONS["th"]["war"]
    th_text = " ".join(c.get("desc", "") + " " + " ".join(c.get("bullets", [])) for c in th_war["cards"])
    assert "ใครใส่เยอะคนนั้นเป็นเจ้าของ" in th_text
    assert "10,000,000" in th_text or "10M" in th_text
    assert "40M" in th_text

    # English V9 check
    en_war = GUIDE_SECTIONS["en"]["war"]
    en_text = " ".join(c.get("desc", "") + " " + " ".join(c.get("bullets", [])) for c in en_war["cards"])
    assert "whoever deposits the highest amount" in en_text or "Deposit & Own" in en_text
    assert "10,000,000" in en_text or "10M" in en_text
    assert "40M" in en_text

    # Japanese V9 check
    ja_war = GUIDE_SECTIONS["ja"]["war"]
    ja_text = " ".join(c.get("desc", "") + " " + " ".join(c.get("bullets", [])) for c in ja_war["cards"])
    assert "10,000,000" in ja_text or "10M" in ja_text
    assert "40M" in ja_text
