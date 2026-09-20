using System;

namespace NekoTracker.Security
{
    public enum TamperViolationType
    {
        None = 0,
        GameProcessNotRunning,
        TimestampSkewOutOfRange,
        TimestampReplayOld,
        SequenceNumberDecreased,
        SequenceJumpAnomalous,
        CharacterIdentityMismatch,
        DropAmountExceedsCeiling,
        VelocityExceedsPhysicalLimit,
        FileStreamTruncated,
        FileStreamTampered
    }

    public class TamperViolation
    {
        public TamperViolationType Type { get; }
        public string Message { get; }
        public DateTime Timestamp { get; }
        public string? LogLine { get; }
        public bool IsFatal { get; }

        public TamperViolation(TamperViolationType type, string message, string? logLine = null, bool isFatal = true)
        {
            Type = type;
            Message = message;
            Timestamp = DateTime.UtcNow;
            LogLine = logLine;
            IsFatal = isFatal;
        }

        public override string ToString() => $"[TamperViolation:{Type}] {Message} (Fatal: {IsFatal})";
    }
}
