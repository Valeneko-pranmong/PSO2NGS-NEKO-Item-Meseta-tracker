using System;
using Xunit;
using NekoTracker.Common;

namespace NekoTracker.Tests
{
    public class VersioningTests
    {
        [Fact]
        public void AppVersion_ShouldExpose_V7Alpha()
        {
            Assert.Equal("Alpha", AppVersion.Channel);
            Assert.Contains("7.0.0", AppVersion.SemVer);
            Assert.Contains("V7.0.0", AppVersion.DisplayVersion);
            Assert.Contains("Alpha", AppVersion.DisplayVersion);
            Assert.Contains("NEKO Item & Meseta Tracker", AppVersion.FullTitle);
        }

        [Theory]
        [InlineData("7.0.0-alpha", "7.0.0", -1)] // Alpha < Final release
        [InlineData("7.0.0", "7.0.0", 0)]
        [InlineData("7.1.0", "7.0.0", 1)]
        [InlineData("6.1.0", "7.0.0-alpha", -1)] // V6 < V7-alpha
        public void AppVersion_CompareSemVer_ShouldEvaluateCorrectPrecedence(string v1, string v2, int expectedSign)
        {
            int result = AppVersion.CompareSemVer(v1, v2);
            int normalized = result < 0 ? -1 : (result > 0 ? 1 : 0);
            Assert.Equal(expectedSign, normalized);
        }
    }
}
