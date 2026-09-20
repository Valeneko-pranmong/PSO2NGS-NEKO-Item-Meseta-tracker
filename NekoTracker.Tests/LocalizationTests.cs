using System;
using Xunit;
using NekoTracker.Localization;

namespace NekoTracker.Tests
{
    public class LocalizationTests
    {
        [Fact]
        public void LanguageManager_ShouldSupport_ThreeLanguages()
        {
            Assert.Contains(LanguageManager.LangEn, LanguageManager.SupportedLanguages);
            Assert.Contains(LanguageManager.LangTh, LanguageManager.SupportedLanguages);
            Assert.Contains(LanguageManager.LangJa, LanguageManager.SupportedLanguages);
        }

        [Fact]
        public void LanguageManager_SwitchLanguage_ShouldUpdateStrings()
        {
            var mgr = LanguageManager.Instance;

            mgr.CurrentLanguage = LanguageManager.LangEn;
            string enTitle = mgr.GetString("SelectLogFolder");
            Assert.Equal("Select Log Folder", enTitle);

            mgr.CurrentLanguage = LanguageManager.LangTh;
            string thTitle = mgr.GetString("SelectLogFolder");
            Assert.Equal("เลือกโฟลเดอร์ Log", thTitle);

            mgr.CurrentLanguage = LanguageManager.LangJa;
            string jaTitle = mgr.GetString("SelectLogFolder");
            Assert.Equal("ログフォルダーを選択", jaTitle);
        }

        [Fact]
        public void LanguageManager_MissingKey_ShouldFallbackToEnglishOrKey()
        {
            var mgr = LanguageManager.Instance;
            mgr.CurrentLanguage = LanguageManager.LangTh;

            // Non-existent key should return the key itself
            string missing = mgr.GetString("NonExistentTestKey_123");
            Assert.Equal("NonExistentTestKey_123", missing);
        }

        [Theory]
        [InlineData("AppTitle")]
        [InlineData("SelectLogFolder")]
        [InlineData("SessionIncome")]
        [InlineData("MesetaPerHour")]
        [InlineData("GadgetMode")]
        [InlineData("AntiTamperSecure")]
        [InlineData("AntiTamperCompromised")]
        public void LanguageManager_CoreKeys_ShouldExistInAllThreeLanguages(string key)
        {
            var mgr = LanguageManager.Instance;

            mgr.CurrentLanguage = LanguageManager.LangEn;
            string en = mgr.GetString(key);
            Assert.False(string.IsNullOrWhiteSpace(en));
            Assert.NotEqual(key, en);

            mgr.CurrentLanguage = LanguageManager.LangTh;
            string th = mgr.GetString(key);
            Assert.False(string.IsNullOrWhiteSpace(th));
            Assert.NotEqual(key, th);

            mgr.CurrentLanguage = LanguageManager.LangJa;
            string ja = mgr.GetString(key);
            Assert.False(string.IsNullOrWhiteSpace(ja));
            Assert.NotEqual(key, ja);
        }
    }
}
