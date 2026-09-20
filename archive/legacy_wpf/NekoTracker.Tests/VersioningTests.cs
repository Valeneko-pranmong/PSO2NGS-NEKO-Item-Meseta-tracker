using System;
using Xunit;
using NekoTracker.Common;

namespace NekoTracker.Tests
{
    public class VersioningTests
    {
        [Fact]
        public void AppVersion_ShouldExpose_V7_1_0()
        {
            Assert.Equal("Release", AppVersion.Channel);
            Assert.Contains("7.1.0", AppVersion.SemVer);
            Assert.Contains("V7.1.0", AppVersion.DisplayVersion);
            Assert.Contains("NEKO Item & Meseta Tracker", AppVersion.FullTitle);
        }

        [Theory]
        [InlineData("7.0.0-alpha", "7.0.0", -1)] // Alpha < Final release
        [InlineData("7.0.0", "7.0.0", 0)]
        [InlineData("7.1.0", "7.0.0", 1)]
        [InlineData("6.1.0", "7.0.0-alpha", -1)] // V6 < V7-alpha
        [InlineData("7.0.0-alpha", "7.1.0", -1)]
        [InlineData("7.1.0", "7.1.0", 0)]
        [InlineData("7.2.0", "7.1.0", 1)]
        public void AppVersion_CompareSemVer_ShouldEvaluateCorrectPrecedence(string v1, string v2, int expectedSign)
        {
            int result = AppVersion.CompareSemVer(v1, v2);
            int normalized = result < 0 ? -1 : (result > 0 ? 1 : 0);
            Assert.Equal(expectedSign, normalized);
        }

        [Theory]
        [InlineData("7.0.0-alpha", false)] // Insecure / Revoked
        [InlineData("7.0.0", false)]       // Insecure / Revoked
        [InlineData("6.1.0", false)]       // Below min secure version
        [InlineData("7.1.0", true)]        // Secure current version
        [InlineData("7.1.1", true)]        // Secure patch
        [InlineData("7.2.0", true)]        // Secure future version
        [InlineData("", false)]            // Empty
        [InlineData(null, false)]          // Null
        public void AppVersion_IsVersionSecure_ShouldVerifyAgainstSecurityPolicy(string? version, bool expectedValid)
        {
            Assert.Equal(expectedValid, AppVersion.IsVersionSecure(version));
        }

        [Fact]
        public void AppVersion_RemotePolicy_ShouldUpdateVersionGateDynamically()
        {
            // Apply dynamic remote policy with higher min version and new revoked
            AppVersion.ApplyRemotePolicy(
                latest: "7.2.0",
                minSecure: "7.1.5",
                revoked: new[] { "7.1.0" }
            );

            Assert.True(AppVersion.RemotePolicyLoaded);
            Assert.Equal("7.2.0", AppVersion.LatestVersion);
            Assert.Equal("7.1.5", AppVersion.DynamicMinSecureVersion);

            // 7.1.0 is now revoked dynamically
            Assert.False(AppVersion.IsVersionSecure("7.1.0"));
            var status710 = AppVersion.EvaluateVersionStatus("7.1.0");
            Assert.Equal(AppVersion.ClientVersionStatus.RevokedInsecure, status710.Status);

            // 7.1.2 is below 7.1.5 minSecure
            Assert.False(AppVersion.IsVersionSecure("7.1.2"));
            var status712 = AppVersion.EvaluateVersionStatus("7.1.2");
            Assert.Equal(AppVersion.ClientVersionStatus.OutdatedInsecure, status712.Status);

            // 7.1.6 is secure but update available
            Assert.True(AppVersion.IsVersionSecure("7.1.6"));
            var status716 = AppVersion.EvaluateVersionStatus("7.1.6");
            Assert.Equal(AppVersion.ClientVersionStatus.UpdateAvailable, status716.Status);

            // 7.2.0 is latest and secure
            Assert.True(AppVersion.IsVersionSecure("7.2.0"));
            var status720 = AppVersion.EvaluateVersionStatus("7.2.0");
            Assert.Equal(AppVersion.ClientVersionStatus.SecureLatest, status720.Status);

            // Reset back for subsequent tests
            AppVersion.DynamicRevokedVersions.Remove("7.1.0");
            AppVersion.ApplyRemotePolicy("7.1.0", "7.1.0", null);
        }
    }
}
