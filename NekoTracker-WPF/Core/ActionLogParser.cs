using System;
using System.Text.RegularExpressions;

namespace NekoTracker.Core
{
    public static class ActionLogParser
    {
        private static readonly Regex MesetaRegex = new(
            @"\t(?:N-)?Meseta\s*\(\s*(\d+)\s*\)",
            RegexOptions.Compiled | RegexOptions.IgnoreCase);

        private static readonly Regex WalletRegex = new(
            @"\tCurrent(?:N-)?Meseta\s*\(\s*(\d+)\s*\)",
            RegexOptions.Compiled | RegexOptions.IgnoreCase);

        private static readonly Regex ItemRegex = new(
            @"\t([^\t]+)\tNum\((\d+)\)",
            RegexOptions.Compiled);

        public static ActionLogRecord? ParseLine(string line)
        {
            if (string.IsNullOrWhiteSpace(line))
                return null;

            var record = new ActionLogRecord
            {
                RawLine = line
            };

            string[] parts = line.Trim().Split('\t');
            if (parts.Length < 3)
                return null;

            // 1. Timestamp (parts[0])
            if (DateTime.TryParse(parts[0].Trim(), out var dt))
            {
                record.Timestamp = dt;
            }

            // 2. Sequence Number (parts[1])
            if (long.TryParse(parts[1].Trim(), out var seq))
            {
                record.SequenceNumber = seq;
            }

            // 3. Action Tag (parts[2])
            record.Action = parts[2].Trim();

            // 4. Player ID (parts[3]) & Character Name (parts[4])
            if (parts.Length >= 5 && long.TryParse(parts[3].Trim(), out _))
            {
                record.PlayerId = parts[3].Trim();
                string cname = parts[4].Trim();
                if (!string.IsNullOrEmpty(cname) && !cname.StartsWith("[") && !cname.Contains("Num("))
                {
                    record.CharacterName = cname;
                }
            }

            // 5. Meseta Drop extraction
            var mesetaMatch = MesetaRegex.Match(line);
            if (mesetaMatch.Success && long.TryParse(mesetaMatch.Groups[1].Value, out long drop))
            {
                record.MesetaDrop = drop;
            }

            // 6. Current Wallet extraction
            var walletMatch = WalletRegex.Match(line);
            if (walletMatch.Success && long.TryParse(walletMatch.Groups[1].Value, out long wallet))
            {
                record.CurrentWallet = wallet;
                record.HasWalletUpdate = true;
            }

            // 7. Item Drop extraction
            // Only extract item if line has Num(x) and not just Meseta
            if (!mesetaMatch.Success && line.Contains("Num("))
            {
                var itemMatch = ItemRegex.Match(line);
                if (itemMatch.Success)
                {
                    string itemName = itemMatch.Groups[1].Value.Trim();
                    if (int.TryParse(itemMatch.Groups[2].Value, out int count) &&
                        !string.IsNullOrEmpty(itemName) &&
                        !itemName.StartsWith("[") &&
                        !itemName.Contains("Meseta"))
                    {
                        record.ItemName = itemName;
                        record.ItemCount = count;
                    }
                }
            }

            return record;
        }

        public static bool IsValidFarmingAction(string action, bool hasWalletUpdate, string rawLine)
        {
            if (action.Contains("[Pickup]") ||
                action.Contains("[AutoSell]") ||
                action.Contains("[Reward]") ||
                action.Contains("[Clear]"))
            {
                return true;
            }

            if (hasWalletUpdate && !rawLine.Contains("["))
            {
                return true;
            }

            return false;
        }
    }
}
