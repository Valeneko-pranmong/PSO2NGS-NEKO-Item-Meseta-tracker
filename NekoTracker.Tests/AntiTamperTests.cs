using System;
using Xunit;
using NekoTracker.Core;
using NekoTracker.Security;

namespace NekoTracker.Tests
{
    public class MockProcessValidator : IProcessValidator
    {
        public bool IsRunning { get; set; } = true;
        public bool IsGameProcessRunning() => IsRunning;
    }

    public class AntiTamperTests
    {
        [Fact]
        public void Layer1_ProcessValidator_ShouldRejectDropsWhenGameNotRunning()
        {
            var mockProcess = new MockProcessValidator { IsRunning = false };
            var guard = new AntiTamperGuard(mockProcess)
            {
                EnforceTimestampValidation = false
            };

            var record = new ActionLogRecord
            {
                Action = "[Pickup]",
                MesetaDrop = 1500,
                RawLine = "dummy log line"
            };

            bool isValid = guard.ValidateRecord(record);
            Assert.False(isValid);
            Assert.True(guard.IsCompromised);
            Assert.Contains(guard.Violations, v => v.Type == TamperViolationType.GameProcessNotRunning);
        }

        [Fact]
        public void Layer2_TimestampValidation_ShouldRejectFutureAndOldTimestamps()
        {
            var mockProcess = new MockProcessValidator { IsRunning = true };
            var guard = new AntiTamperGuard(mockProcess);
            var now = new DateTime(2026, 9, 20, 12, 0, 0);

            // Future timestamp (+ 5 minutes)
            var futureRecord = new ActionLogRecord
            {
                Timestamp = now.AddMinutes(5),
                MesetaDrop = 500,
                Action = "[Pickup]"
            };
            Assert.False(guard.ValidateRecord(futureRecord, referenceTime: now));
            Assert.Contains(guard.Violations, v => v.Type == TamperViolationType.TimestampSkewOutOfRange);

            guard.Reset();

            // Too old timestamp (- 10 minutes)
            var oldRecord = new ActionLogRecord
            {
                Timestamp = now.AddMinutes(-10),
                MesetaDrop = 500,
                Action = "[Pickup]"
            };
            Assert.False(guard.ValidateRecord(oldRecord, referenceTime: now));
            Assert.Contains(guard.Violations, v => v.Type == TamperViolationType.TimestampReplayOld);
        }

        [Fact]
        public void Layer3_SequenceValidation_ShouldRejectDecreasingSequence()
        {
            var mockProcess = new MockProcessValidator { IsRunning = true };
            var guard = new AntiTamperGuard(mockProcess)
            {
                EnforceTimestampValidation = false
            };

            var rec1 = new ActionLogRecord { SequenceNumber = 100, MesetaDrop = 100 };
            var rec2 = new ActionLogRecord { SequenceNumber = 101, MesetaDrop = 100 };
            var rec3 = new ActionLogRecord { SequenceNumber = 95, MesetaDrop = 100 }; // Decreased!

            Assert.True(guard.ValidateRecord(rec1));
            Assert.True(guard.ValidateRecord(rec2));
            Assert.False(guard.ValidateRecord(rec3));
            Assert.Contains(guard.Violations, v => v.Type == TamperViolationType.SequenceNumberDecreased);
        }

        [Fact]
        public void Layer4_CeilingAndVelocity_ShouldRejectGiantDropAndExcessiveSpeed()
        {
            var mockProcess = new MockProcessValidator { IsRunning = true };
            var guard = new AntiTamperGuard(mockProcess)
            {
                EnforceTimestampValidation = false,
                MaxSingleMesetaDrop = 100_000,
                MaxMesetaPerMinute = 200_000
            };

            // Single drop over ceiling
            var giantDrop = new ActionLogRecord { MesetaDrop = 999_999 };
            Assert.False(guard.ValidateRecord(giantDrop));
            Assert.Contains(guard.Violations, v => v.Type == TamperViolationType.DropAmountExceedsCeiling);

            guard.Reset();

            // Velocity flood within 1 minute
            var t0 = new DateTime(2026, 9, 20, 12, 0, 0);
            Assert.True(guard.ValidateRecord(new ActionLogRecord { Timestamp = t0, MesetaDrop = 80_000 }, t0));
            Assert.True(guard.ValidateRecord(new ActionLogRecord { Timestamp = t0.AddSeconds(10), MesetaDrop = 80_000 }, t0.AddSeconds(10)));
            // 80k + 80k + 80k = 240k > 200k limit!
            Assert.False(guard.ValidateRecord(new ActionLogRecord { Timestamp = t0.AddSeconds(20), MesetaDrop = 80_000 }, t0.AddSeconds(20)));
            Assert.Contains(guard.Violations, v => v.Type == TamperViolationType.VelocityExceedsPhysicalLimit);
        }

        [Fact]
        public void Layer5_StreamIntegrity_ShouldDetectFileShrinkAndRewind()
        {
            var guard = new AntiTamperGuard();

            Assert.True(guard.ValidateStream(1000, 2000));
            Assert.True(guard.ValidateStream(2000, 3000));

            // File shrank from 3000 to 1500 (file truncated/modified externally)
            Assert.False(guard.ValidateStream(1500, 1500));
            Assert.Contains(guard.Violations, v => v.Type == TamperViolationType.FileStreamTruncated);
        }
    }
}
