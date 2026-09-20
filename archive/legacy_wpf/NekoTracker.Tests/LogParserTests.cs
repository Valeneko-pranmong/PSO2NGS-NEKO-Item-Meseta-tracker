using System;
using Xunit;
using NekoTracker.Core;

namespace NekoTracker.Tests
{
    public class LogParserTests
    {
        [Fact]
        public void ParseLine_ValidPickup_ShouldExtractMesetaAndCharacter()
        {
            string line = "2026-09-19T20:00:11\t102\t[Pickup]\t14743890\tVale3neko\tN-Meseta(1500)\tNum(1)\n";
            var record = ActionLogParser.ParseLine(line);

            Assert.NotNull(record);
            Assert.Equal("14743890", record!.PlayerId);
            Assert.Equal("Vale3neko", record.CharacterName);
            Assert.Equal("[Pickup]", record.Action);
            Assert.Equal(1500, record.MesetaDrop);
            Assert.Equal(102, record.SequenceNumber);
        }

        [Fact]
        public void ParseLine_ItemDrop_ShouldExtractItemNameAndCount()
        {
            string line = "2026-09-19T20:05:30\t105\t[Pickup]\t14743890\tVale3neko\tC/Astraea II\tNum(2)\n";
            var record = ActionLogParser.ParseLine(line);

            Assert.NotNull(record);
            Assert.Equal("C/Astraea II", record!.ItemName);
            Assert.Equal(2, record.ItemCount);
            Assert.Equal(0, record.MesetaDrop);
        }

        [Fact]
        public void ParseLine_JapaneseItemDrop_ShouldExtractJapaneseCharacters()
        {
            string line = "2026-09-19T20:06:15\t106\t[Pickup]\t14743890\tネコちゃん\tC/アストレアII\tNum(1)\n";
            var record = ActionLogParser.ParseLine(line);

            Assert.NotNull(record);
            Assert.Equal("ネコちゃん", record!.CharacterName);
            Assert.Equal("C/アストレアII", record.ItemName);
            Assert.Equal(1, record.ItemCount);
        }

        [Fact]
        public void ParseLine_CurrentWalletUpdate_ShouldExtractWallet()
        {
            string line = "2026-09-19T20:00:12\t103\t[Pickup]\t14743890\tVale3neko\tN-Meseta(1500)\tCurrentN-Meseta(25000000)\n";
            var record = ActionLogParser.ParseLine(line);

            Assert.NotNull(record);
            Assert.Equal(1500, record!.MesetaDrop);
            Assert.Equal(25000000, record.CurrentWallet);
            Assert.True(record.HasWalletUpdate);
        }
    }

    public class TrackerStatsTests
    {
        [Fact]
        public void TrackerStats_IncomeCalculation_ShouldAccumulateMeseta()
        {
            var stats = new TrackerStats();

            stats.ProcessRecord(new ActionLogRecord
            {
                CharacterName = "Vale3neko",
                PlayerId = "14743890",
                MesetaDrop = 1000,
                CurrentWallet = 10000,
                HasWalletUpdate = true
            });

            Assert.Equal(1000, stats.SessionMeseta);
            Assert.Equal(10000, stats.CurrentWallet);

            stats.ProcessRecord(new ActionLogRecord
            {
                MesetaDrop = 2500,
                CurrentWallet = 12500,
                HasWalletUpdate = true
            });

            Assert.Equal(3500, stats.SessionMeseta);
            Assert.Equal(12500, stats.CurrentWallet);
        }

        [Fact]
        public void TrackerStats_Formatting_ShouldFormatCompactAndRates()
        {
            Assert.Equal("1.50M", TrackerStats.FormatCompact(1500000));
            Assert.Equal("25.0k", TrackerStats.FormatCompact(25000));
            Assert.Equal("500", TrackerStats.FormatCompact(500));

            Assert.Equal("2.50 M/hr", TrackerStats.FormatRate(2500000));
            Assert.Equal("50.0 k/hr", TrackerStats.FormatRate(50000));
            Assert.Equal("0 /hr", TrackerStats.FormatRate(0));

            Assert.Equal("01:05:30", TrackerStats.FormatDuration(new TimeSpan(1, 5, 30)));
        }
    }
}
