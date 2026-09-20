using System;
using System.Collections.Generic;
using NekoTracker.Core;

namespace NekoTracker.Security
{
    public class AntiTamperGuard
    {
        private readonly IProcessValidator _processValidator;

        // Configuration & Thresholds
        public long MaxSingleMesetaDrop { get; set; } = 300_000;          // Max realistic single drop
        public long MaxMesetaPerMinute { get; set; } = 250_000;            // ~15M/hr ceiling (impossible in NGS)
        public TimeSpan MaxFutureTimestampSkew { get; set; } = TimeSpan.FromSeconds(60);
        public TimeSpan MaxPastTimestampSkew { get; set; } = TimeSpan.FromMinutes(5);
        public bool EnforceProcessValidation { get; set; } = true;
        public bool EnforceTimestampValidation { get; set; } = true;

        // Tracking state
        private long _lastSequence = -1;
        private DateTime _lastTimestamp = DateTime.MinValue;
        private string? _lockedPlayerId = null;
        private string? _lockedCharacterName = null;

        private long _lastFileSize = 0;
        private long _lastFilePosition = 0;

        // Sliding window for velocity check: (Timestamp, MesetaAmount)
        private readonly Queue<(DateTime Timestamp, long Amount)> _velocityWindow = new();
        private long _windowMesetaTotal = 0;

        // Events
        public event Action<TamperViolation>? OnViolation;
        public bool IsCompromised { get; private set; } = false;
        public List<TamperViolation> Violations { get; } = new();

        public AntiTamperGuard(IProcessValidator? processValidator = null)
        {
            _processValidator = processValidator ?? new WindowsProcessValidator();
        }

        public void Reset()
        {
            _lastSequence = -1;
            _lastTimestamp = DateTime.MinValue;
            _lockedPlayerId = null;
            _lockedCharacterName = null;
            _lastFileSize = 0;
            _lastFilePosition = 0;
            _velocityWindow.Clear();
            _windowMesetaTotal = 0;
            IsCompromised = false;
            Violations.Clear();
        }

        public void LockIdentity(string playerId, string characterName)
        {
            _lockedPlayerId = playerId;
            _lockedCharacterName = characterName;
        }

        /// <summary>
        /// Validates file stream continuity before reading.
        /// Catches file shrinking, truncation, or unexpected rewind.
        /// </summary>
        public bool ValidateStream(long currentFilePosition, long currentFileSize)
        {
            if (_lastFileSize > 0 && currentFileSize < _lastFileSize)
            {
                RecordViolation(new TamperViolation(
                    TamperViolationType.FileStreamTruncated,
                    $"File size shrank from {_lastFileSize} to {currentFileSize}. Log file was truncated or modified externally."
                ));
                return false;
            }

            if (_lastFilePosition > 0 && currentFilePosition < _lastFilePosition)
            {
                RecordViolation(new TamperViolation(
                    TamperViolationType.FileStreamTampered,
                    $"File read position rewound from {_lastFilePosition} to {currentFilePosition}."
                ));
                return false;
            }

            _lastFileSize = currentFileSize;
            _lastFilePosition = currentFilePosition;
            return true;
        }

        /// <summary>
        /// Validates a parsed ActionLog record across all security gates.
        /// </summary>
        public bool ValidateRecord(ActionLogRecord record, DateTime? referenceTime = null)
        {
            var now = referenceTime ?? DateTime.Now;

            // 1. Game Process Verification
            if (EnforceProcessValidation && (record.HasMesetaDrop || record.HasItemDrop))
            {
                if (!_processValidator.IsGameProcessRunning())
                {
                    RecordViolation(new TamperViolation(
                        TamperViolationType.GameProcessNotRunning,
                        "Meseta/Item recorded while PSO2 game process is not running. Suspected fake log injection.",
                        record.RawLine
                    ));
                    return false;
                }
            }

            // 2. Timestamp Verification
            if (EnforceTimestampValidation && record.Timestamp > DateTime.MinValue)
            {
                if (record.Timestamp > now.Add(MaxFutureTimestampSkew))
                {
                    RecordViolation(new TamperViolation(
                        TamperViolationType.TimestampSkewOutOfRange,
                        $"Record timestamp is in the future: {record.Timestamp:s} (Current: {now:s}).",
                        record.RawLine
                    ));
                    return false;
                }

                if (now - record.Timestamp > MaxPastTimestampSkew)
                {
                    RecordViolation(new TamperViolation(
                        TamperViolationType.TimestampReplayOld,
                        $"Record timestamp is too old (> {MaxPastTimestampSkew.TotalMinutes} mins): {record.Timestamp:s}.",
                        record.RawLine
                    ));
                    return false;
                }

                if (_lastTimestamp > DateTime.MinValue && record.Timestamp < _lastTimestamp.AddSeconds(-2))
                {
                    RecordViolation(new TamperViolation(
                        TamperViolationType.TimestampSkewOutOfRange,
                        $"Record timestamp moved backward from {_lastTimestamp:s} to {record.Timestamp:s}.",
                        record.RawLine
                    ));
                    return false;
                }
            }

            // 3. Sequence Monotonicity
            if (record.SequenceNumber >= 0)
            {
                if (_lastSequence >= 0)
                {
                    if (record.SequenceNumber < _lastSequence)
                    {
                        RecordViolation(new TamperViolation(
                            TamperViolationType.SequenceNumberDecreased,
                            $"Log sequence number decreased from {_lastSequence} to {record.SequenceNumber}.",
                            record.RawLine
                        ));
                        return false;
                    }

                    if (record.SequenceNumber - _lastSequence > 5000)
                    {
                        RecordViolation(new TamperViolation(
                            TamperViolationType.SequenceJumpAnomalous,
                            $"Suspicious jump in sequence number from {_lastSequence} to {record.SequenceNumber}.",
                            record.RawLine,
                            isFatal: false
                        ));
                    }
                }
                _lastSequence = record.SequenceNumber;
            }

            // 4. Character Identity Consistency
            if (!string.IsNullOrEmpty(_lockedCharacterName) && !string.IsNullOrEmpty(record.CharacterName))
            {
                if (!string.Equals(record.CharacterName, _lockedCharacterName, StringComparison.OrdinalIgnoreCase))
                {
                    RecordViolation(new TamperViolation(
                        TamperViolationType.CharacterIdentityMismatch,
                        $"Character name mismatch: Expected '{_lockedCharacterName}' but got '{record.CharacterName}'.",
                        record.RawLine
                    ));
                    return false;
                }
            }

            // 5. Drop Limits & Velocity Gates
            if (record.HasMesetaDrop)
            {
                if (record.MesetaDrop > MaxSingleMesetaDrop)
                {
                    RecordViolation(new TamperViolation(
                        TamperViolationType.DropAmountExceedsCeiling,
                        $"Single Meseta drop of {record.MesetaDrop:N0} exceeds maximum ceiling of {MaxSingleMesetaDrop:N0}.",
                        record.RawLine
                    ));
                    return false;
                }

                // Update sliding window (1 minute)
                DateTime eventTime = record.Timestamp > DateTime.MinValue ? record.Timestamp : now;
                _velocityWindow.Enqueue((eventTime, record.MesetaDrop));
                _windowMesetaTotal += record.MesetaDrop;

                DateTime windowCutoff = eventTime.AddMinutes(-1);
                while (_velocityWindow.Count > 0 && _velocityWindow.Peek().Timestamp < windowCutoff)
                {
                    var old = _velocityWindow.Dequeue();
                    _windowMesetaTotal -= old.Amount;
                }

                if (_windowMesetaTotal > MaxMesetaPerMinute)
                {
                    RecordViolation(new TamperViolation(
                        TamperViolationType.VelocityExceedsPhysicalLimit,
                        $"Meseta farming velocity {_windowMesetaTotal:N0}/min exceeds physical maximum ceiling of {MaxMesetaPerMinute:N0}/min.",
                        record.RawLine
                    ));
                    return false;
                }
            }

            if (record.Timestamp > DateTime.MinValue)
            {
                _lastTimestamp = record.Timestamp;
            }

            return true;
        }

        private void RecordViolation(TamperViolation violation)
        {
            Violations.Add(violation);
            if (violation.IsFatal)
            {
                IsCompromised = true;
            }
            OnViolation?.Invoke(violation);
        }
    }
}
