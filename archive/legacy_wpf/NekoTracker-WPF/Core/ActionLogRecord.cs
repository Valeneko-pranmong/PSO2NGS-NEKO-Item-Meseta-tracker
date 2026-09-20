using System;

namespace NekoTracker.Core
{
    public class ActionLogRecord
    {
        public string RawLine { get; set; } = string.Empty;
        public DateTime Timestamp { get; set; } = DateTime.MinValue;
        public long SequenceNumber { get; set; } = -1;
        public string Action { get; set; } = string.Empty;
        public string PlayerId { get; set; } = string.Empty;
        public string CharacterName { get; set; } = string.Empty;

        public long MesetaDrop { get; set; } = 0;
        public long CurrentWallet { get; set; } = 0;
        public bool HasWalletUpdate { get; set; } = false;

        public string? ItemName { get; set; }
        public int ItemCount { get; set; } = 0;

        public bool HasMesetaDrop => MesetaDrop > 0;
        public bool HasItemDrop => !string.IsNullOrEmpty(ItemName) && ItemCount > 0;
        public bool IsValidAction => !string.IsNullOrEmpty(Action);
    }
}
