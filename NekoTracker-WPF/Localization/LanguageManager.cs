using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Globalization;
using System.IO;
using System.Text.Json;

namespace NekoTracker.Localization
{
    public class LanguageManager : INotifyPropertyChanged
    {
        public const string LangEn = "en";
        public const string LangTh = "th";
        public const string LangJa = "ja";

        public static readonly string[] SupportedLanguages = { LangEn, LangTh, LangJa };

        public static LanguageManager Instance { get; } = new LanguageManager();

        private string _currentLanguage = LangEn;
        private readonly Dictionary<string, Dictionary<string, string>> _translations = new();

        public event PropertyChangedEventHandler? PropertyChanged;
        public event Action<string>? OnLanguageChanged;

        public string CurrentLanguage
        {
            get => _currentLanguage;
            set
            {
                if (Array.IndexOf(SupportedLanguages, value) >= 0 && _currentLanguage != value)
                {
                    _currentLanguage = value;
                    PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("Item[]"));
                    PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nameof(CurrentLanguage)));
                    OnLanguageChanged?.Invoke(_currentLanguage);
                }
            }
        }

        public string this[string key] => GetString(key);

        public LanguageManager()
        {
            InitializeBuiltInTranslations();
            _currentLanguage = DetectInitialLanguage();
        }

        public string DetectInitialLanguage()
        {
            try
            {
                string twoLetter = CultureInfo.CurrentUICulture.TwoLetterISOLanguageName.ToLowerInvariant();
                if (twoLetter == "th") return LangTh;
                if (twoLetter == "ja") return LangJa;
            }
            catch
            {
                // Fallback to English
            }

            return LangEn;
        }

        public string GetString(string key)
        {
            if (string.IsNullOrEmpty(key)) return string.Empty;

            // 1. Try current language
            if (_translations.TryGetValue(_currentLanguage, out var currentDict) &&
                currentDict.TryGetValue(key, out var val))
            {
                return val;
            }

            // 2. Fallback to English
            if (_translations.TryGetValue(LangEn, out var enDict) &&
                enDict.TryGetValue(key, out var enVal))
            {
                return enVal;
            }

            return key;
        }

        private void InitializeBuiltInTranslations()
        {
            _translations[LangEn] = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
            {
                ["AppTitle"] = "NEKO Item & Meseta Tracker",
                ["SelectLogFolder"] = "Select Log Folder",
                ["LogStatusConnected"] = "Monitoring Active",
                ["LogStatusWaiting"] = "Waiting for Log...",
                ["SessionIncome"] = "Session Income",
                ["CurrentWallet"] = "Current Wallet",
                ["MesetaPerHour"] = "Meseta / hr",
                ["FarmingDuration"] = "Farming Time",
                ["TotalDrops"] = "Item Drops",
                ["WatchlistFilter"] = "Watchlist Only",
                ["SearchPlaceholder"] = "Search item name...",
                ["GadgetMode"] = "Gadget Overlay",
                ["ClickThrough"] = "Click Through",
                ["Opacity"] = "Opacity",
                ["AntiTamperSecure"] = "Security: Verified & Safe",
                ["AntiTamperCompromised"] = "Security: Tamper Detected!",
                ["Language"] = "Language",
                ["Close"] = "Close",
                ["Minimize"] = "Minimize",
                ["Character"] = "Character",
                ["PlayerId"] = "Player ID",
                ["ResetSession"] = "Reset Session",
                ["ItemName"] = "Item Name",
                ["Count"] = "Count"
            };

            _translations[LangTh] = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
            {
                ["AppTitle"] = "NEKO Item & Meseta Tracker",
                ["SelectLogFolder"] = "เลือกโฟลเดอร์ Log",
                ["LogStatusConnected"] = "กำลังติดตามข้อมูล Real-time",
                ["LogStatusWaiting"] = "รอไฟล์ Log ของเกม...",
                ["SessionIncome"] = "รายได้รอบนี้",
                ["CurrentWallet"] = "กระเป๋าปัจจุบัน",
                ["MesetaPerHour"] = "ความเร็ว / ชม.",
                ["FarmingDuration"] = "เวลาฟาร์ม",
                ["TotalDrops"] = "รายการไอเทมดรอป",
                ["WatchlistFilter"] = "เฉพาะไอเทมสนใจ",
                ["SearchPlaceholder"] = "ค้นหาชื่อไอเทม...",
                ["GadgetMode"] = "โหมด Gadget (Overlay)",
                ["ClickThrough"] = "คลิกทะลุจอ",
                ["Opacity"] = "ความโปร่งใส",
                ["AntiTamperSecure"] = "ระบบความปลอดภัย: ปกติ",
                ["AntiTamperCompromised"] = "ระบบความปลอดภัย: ตรวจพบการดัดแปลง!",
                ["Language"] = "ภาษา",
                ["Close"] = "ปิด",
                ["Minimize"] = "ย่อหน้าต่าง",
                ["Character"] = "ตัวละคร",
                ["PlayerId"] = "รหัสผู้เล่น",
                ["ResetSession"] = "รีเซ็ตสถิติ",
                ["ItemName"] = "ชื่อไอเทม",
                ["Count"] = "จำนวน"
            };

            _translations[LangJa] = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
            {
                ["AppTitle"] = "NEKO アイテム・メセタ トラッカー",
                ["SelectLogFolder"] = "ログフォルダーを選択",
                ["LogStatusConnected"] = "リアルタイム監視中",
                ["LogStatusWaiting"] = "ログファイルを待機中...",
                ["SessionIncome"] = "今回の獲得メセタ",
                ["CurrentWallet"] = "現在の所持メセタ",
                ["MesetaPerHour"] = "時給 (メセタ/時)",
                ["FarmingDuration"] = "稼働時間",
                ["TotalDrops"] = "ドロップアイテム一覧",
                ["WatchlistFilter"] = "登録アイテムのみ",
                ["SearchPlaceholder"] = "アイテム名で検索...",
                ["GadgetMode"] = "ガジェット (オーバーレイ)",
                ["ClickThrough"] = "クリックスルー",
                ["Opacity"] = "不透明度",
                ["AntiTamperSecure"] = "セキュリティ: 正常稼働",
                ["AntiTamperCompromised"] = "セキュリティ: 改ざん検知!",
                ["Language"] = "言語",
                ["Close"] = "閉じる",
                ["Minimize"] = "最小化",
                ["Character"] = "キャラクター",
                ["PlayerId"] = "プレイヤーID",
                ["ResetSession"] = "リセット",
                ["ItemName"] = "アイテム名",
                ["Count"] = "個数"
            };
        }
    }
}
