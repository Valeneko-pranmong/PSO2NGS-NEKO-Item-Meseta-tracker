using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;

namespace NekoTracker.Core
{
    public class TrackerStats
    {
        private readonly object _lock = new();

        public long SessionMeseta { get; private set; } = 0;
        public long CurrentWallet { get; private set; } = 0;
        public long InitialWallet { get; private set; } = 0;

        public DateTime? FirstDropTime { get; private set; }
        public DateTime? LastIncomeTime { get; private set; }

        public string CharacterName { get; private set; } = string.Empty;
        public string PlayerId { get; private set; } = string.Empty;

        private readonly Dictionary<string, int> _itemCounts = new(StringComparer.OrdinalIgnoreCase);
        private readonly HashSet<string> _watchlist = new(StringComparer.OrdinalIgnoreCase);
        public bool IsWatchlistOnly { get; set; } = false;

        public event Action? OnStatsUpdated;

        public void Reset()
        {
            lock (_lock)
            {
                SessionMeseta = 0;
                CurrentWallet = 0;
                InitialWallet = 0;
                FirstDropTime = null;
                LastIncomeTime = null;
                CharacterName = string.Empty;
                PlayerId = string.Empty;
                _itemCounts.Clear();
            }
            OnStatsUpdated?.Invoke();
        }

        public void ProcessRecord(ActionLogRecord record)
        {
            bool changed = false;

            lock (_lock)
            {
                // Update character identity
                if (!string.IsNullOrEmpty(record.CharacterName))
                {
                    CharacterName = record.CharacterName;
                }
                if (!string.IsNullOrEmpty(record.PlayerId))
                {
                    PlayerId = record.PlayerId;
                }

                // Process Wallet & Meseta
                if (record.HasWalletUpdate)
                {
                    long newWallet = record.CurrentWallet;
                    long income = 0;

                    if (InitialWallet == 0 && CurrentWallet == 0)
                    {
                        InitialWallet = newWallet;
                        CurrentWallet = newWallet;
                        if (record.HasMesetaDrop)
                        {
                            income = record.MesetaDrop;
                        }
                    }
                    else
                    {
                        if (newWallet > CurrentWallet)
                        {
                            income = newWallet - CurrentWallet;
                        }
                        CurrentWallet = newWallet;
                    }

                    if (income > 0)
                    {
                        if (NekoTracker.Common.AppVersion.IsVersionSecure(NekoTracker.Common.AppVersion.SemVer))
                        {
                            FirstDropTime ??= DateTime.Now;
                            SessionMeseta += income;
                            LastIncomeTime = DateTime.Now;
                        }
                        changed = true;
                    }
                }
                else if (record.HasMesetaDrop)
                {
                    if (NekoTracker.Common.AppVersion.IsVersionSecure(NekoTracker.Common.AppVersion.SemVer))
                    {
                        FirstDropTime ??= DateTime.Now;
                        SessionMeseta += record.MesetaDrop;
                        LastIncomeTime = DateTime.Now;
                    }
                    changed = true;
                }

                // Process Item Drop
                if (record.HasItemDrop && !string.IsNullOrEmpty(record.ItemName))
                {
                    _itemCounts.TryGetValue(record.ItemName, out int existing);
                    _itemCounts[record.ItemName] = existing + record.ItemCount;
                    changed = true;
                }
            }

            if (changed)
            {
                OnStatsUpdated?.Invoke();
            }
        }

        public TimeSpan GetDuration(DateTime? now = null)
        {
            if (FirstDropTime == null) return TimeSpan.Zero;
            var current = now ?? DateTime.Now;
            return current > FirstDropTime.Value ? current - FirstDropTime.Value : TimeSpan.Zero;
        }

        public double GetMesetaPerHour(DateTime? now = null)
        {
            var duration = GetDuration(now);
            if (duration.TotalSeconds < 10 || SessionMeseta <= 0) return 0;
            return (SessionMeseta / duration.TotalSeconds) * 3600.0;
        }

        public IReadOnlyList<(string Name, int Count)> GetFilteredItems(string? search = null)
        {
            lock (_lock)
            {
                var query = _itemCounts.AsEnumerable();

                if (IsWatchlistOnly && _watchlist.Count > 0)
                {
                    query = query.Where(kvp => _watchlist.Contains(kvp.Key));
                }

                if (!string.IsNullOrWhiteSpace(search))
                {
                    query = query.Where(kvp => kvp.Key.IndexOf(search, StringComparison.OrdinalIgnoreCase) >= 0);
                }

                return query
                    .OrderByDescending(kvp => kvp.Value)
                    .Select(kvp => (kvp.Key, kvp.Value))
                    .ToList();
            }
        }

        public void AddToWatchlist(string item)
        {
            lock (_lock) { _watchlist.Add(item.Trim()); }
            OnStatsUpdated?.Invoke();
        }

        public void RemoveFromWatchlist(string item)
        {
            lock (_lock) { _watchlist.Remove(item.Trim()); }
            OnStatsUpdated?.Invoke();
        }

        public bool IsInWatchlist(string item)
        {
            lock (_lock) { return _watchlist.Contains(item.Trim()); }
        }

        // Formatting Helpers
        public static string FormatCompact(long value)
        {
            long abs = Math.Abs(value);
            string sign = value < 0 ? "-" : "";

            if (abs >= 1_000_000)
                return $"{sign}{abs / 1_000_000.0:F2}M";
            if (abs >= 10_000)
                return $"{sign}{abs / 1_000.0:F1}k";
            return $"{sign}{abs:N0}";
        }

        public static string FormatRate(double mPerHour)
        {
            if (mPerHour <= 0) return "0 /hr";
            if (mPerHour >= 1_000_000)
                return $"{mPerHour / 1_000_000.0:F2} M/hr";
            if (mPerHour >= 1_000)
                return $"{mPerHour / 1_000.0:F1} k/hr";
            return $"{mPerHour:N0} /hr";
        }

        public static string FormatDuration(TimeSpan duration)
        {
            int hours = (int)duration.TotalHours;
            return $"{hours:D2}:{duration.Minutes:D2}:{duration.Seconds:D2}";
        }
    }
}
