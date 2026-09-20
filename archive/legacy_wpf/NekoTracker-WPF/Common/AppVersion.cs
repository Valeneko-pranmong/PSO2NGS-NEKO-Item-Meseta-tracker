using System;
using System.Collections.Generic;
using System.Reflection;

namespace NekoTracker.Common
{
    /// <summary>
    /// Centralized application versioning system for NEKO Tracker.
    /// Dynamically reflects assembly metadata defined in project properties.
    /// </summary>
    public static class AppVersion
    {
        public const string Channel = "Release";
        public const string DefaultVersion = "7.1.0";
        public const string MinSecureVersion = "7.1.0";
        public static readonly string[] RevokedVersions = new[] { "7.0.0-alpha", "7.0.0" };

        public static string LatestVersion { get; set; } = DefaultVersion;
        public static string DynamicMinSecureVersion { get; set; } = MinSecureVersion;
        public static HashSet<string> DynamicRevokedVersions { get; } = new(RevokedVersions, StringComparer.OrdinalIgnoreCase);
        public static bool RemotePolicyLoaded { get; private set; } = false;

        public enum ClientVersionStatus
        {
            SecureLatest,
            UpdateAvailable,
            RevokedInsecure,
            OutdatedInsecure
        }

        public static void ApplyRemotePolicy(string? latest, string? minSecure, System.Collections.Generic.IEnumerable<string>? revoked)
        {
            if (!string.IsNullOrWhiteSpace(latest)) LatestVersion = latest.Trim();
            if (!string.IsNullOrWhiteSpace(minSecure)) DynamicMinSecureVersion = minSecure.Trim();
            if (revoked != null)
            {
                foreach (var r in revoked)
                {
                    if (!string.IsNullOrWhiteSpace(r))
                        DynamicRevokedVersions.Add(r.Trim().TrimStart('v', 'V'));
                }
            }
            RemotePolicyLoaded = true;
        }

        public static async System.Threading.Tasks.Task<bool> FetchRemotePolicyAsync(string? firebaseRtdbUrl = null, int timeoutSeconds = 4)
        {
            try
            {
                string baseUrl = (firebaseRtdbUrl ?? "https://arks-war-room-default-rtdb.asia-southeast1.firebasedatabase.app").TrimEnd('/');
                string url = $"{baseUrl}/arks_war_room/version_control.json";

                using var cts = new System.Threading.CancellationTokenSource(TimeSpan.FromSeconds(timeoutSeconds));
                using var client = new System.Net.Http.HttpClient();
                client.DefaultRequestHeaders.UserAgent.ParseAdd($"NEKOTracker-WPF/{SemVer}");

                var response = await client.GetAsync(url, cts.Token);
                if (!response.IsSuccessStatusCode) return false;

                string json = await response.Content.ReadAsStringAsync(cts.Token);
                using var doc = System.Text.Json.JsonDocument.Parse(json);
                var root = doc.RootElement;

                string? latest = root.TryGetProperty("latest_version", out var lProp) ? lProp.GetString() : null;
                string? minSec = root.TryGetProperty("min_secure_version", out var mProp) ? mProp.GetString() : null;
                var revokedList = new System.Collections.Generic.List<string>();

                if (root.TryGetProperty("revoked_versions", out var rProp))
                {
                    if (rProp.ValueKind == System.Text.Json.JsonValueKind.Object)
                    {
                        foreach (var prop in rProp.EnumerateObject())
                        {
                            if (prop.Value.GetBoolean())
                                revokedList.Add(prop.Name.Replace('_', '.'));
                        }
                    }
                    else if (rProp.ValueKind == System.Text.Json.JsonValueKind.Array)
                    {
                        foreach (var el in rProp.EnumerateArray())
                        {
                            var s = el.GetString();
                            if (!string.IsNullOrEmpty(s)) revokedList.Add(s);
                        }
                    }
                }

                ApplyRemotePolicy(latest, minSec, revokedList);
                return true;
            }
            catch
            {
                return false;
            }
        }

        public static (ClientVersionStatus Status, string Message) EvaluateVersionStatus(string? version = null)
        {
            string ver = string.IsNullOrWhiteSpace(version) ? SemVer : version.Trim();
            string clean = ver.TrimStart('v', 'V');

            if (DynamicRevokedVersions.Contains(clean))
            {
                return (ClientVersionStatus.RevokedInsecure,
                    $"เวอร์ชัน {ver} ถูกเพิกถอนเนื่องจากมีปัญหาความปลอดภัย ยอดเงินจะไม่ถูกบันทึก กรุณาอัปเดตเป็น {LatestVersion}");
            }

            if (!IsVersionSecure(ver))
            {
                return (ClientVersionStatus.OutdatedInsecure,
                    $"เวอร์ชัน {ver} ต่ำกว่าเกณฑ์ความปลอดภัยขั้นต่ำ ({DynamicMinSecureVersion}) ยอดเงินจะไม่ถูกบันทึก กรุณาอัปเดตเป็น {LatestVersion}");
            }

            if (CompareSemVer(clean, LatestVersion) < 0)
            {
                return (ClientVersionStatus.UpdateAvailable,
                    $"มีเวอร์ชันใหม่ {LatestVersion} (ปัจจุบัน: {ver}) แนะนำให้อัปเดตเพื่อฟีเจอร์ล่าสุด");
            }

            return (ClientVersionStatus.SecureLatest,
                $"เวอร์ชันปัจจุบัน {ver} เป็นเวอร์ชันล่าสุดและปลอดภัย");
        }

        private static readonly Version _assemblyVersion;
        private static readonly string _informationalVersion;

        static AppVersion()
        {
            var assembly = Assembly.GetExecutingAssembly();
            _assemblyVersion = assembly.GetName().Version ?? new Version(7, 1, 0, 0);

            var infoAttr = assembly.GetCustomAttribute<AssemblyInformationalVersionAttribute>();
            _informationalVersion = infoAttr?.InformationalVersion ?? DefaultVersion;
        }

        public static int Major => _assemblyVersion.Major;
        public static int Minor => _assemblyVersion.Minor;
        public static int Build => _assemblyVersion.Build;
        public static int Revision => _assemblyVersion.Revision;

        /// <summary>
        /// Exact Semantic Version string, e.g. "7.0.0-alpha"
        /// </summary>
        public static string SemVer => _informationalVersion;

        /// <summary>
        /// Formatted display version tag, e.g. "V7.0.0 Alpha"
        /// </summary>
        public static string DisplayVersion
        {
            get
            {
                string tag = SemVer.StartsWith("v", StringComparison.OrdinalIgnoreCase)
                    ? SemVer
                    : $"V{SemVer}";

                // Format "V7.0.0-alpha" -> "V7.0.0 Alpha"
                return tag.Replace("-alpha", " Alpha", StringComparison.OrdinalIgnoreCase)
                          .Replace("-beta", " Beta", StringComparison.OrdinalIgnoreCase)
                          .Replace("-rc", " RC", StringComparison.OrdinalIgnoreCase);
            }
        }

        /// <summary>
        /// Full application title with version tag, e.g. "NEKO Item & Meseta Tracker V7.0.0 Alpha"
        /// </summary>
        public static string FullTitle => $"NEKO Item & Meseta Tracker {DisplayVersion}";

        /// <summary>
        /// Compares two semantic version strings (e.g. "7.0.0-alpha" vs "7.1.0").
        /// Returns -1 if v1 < v2, 0 if equal, 1 if v1 > v2.
        /// </summary>
        public static int CompareSemVer(string v1, string v2)
        {
            var p1 = ParseVersionCore(v1);
            var p2 = ParseVersionCore(v2);

            int cmp = p1.Core.CompareTo(p2.Core);
            if (cmp != 0) return cmp;

            // Pre-release versions have lower precedence than normal version
            bool p1HasPre = !string.IsNullOrEmpty(p1.PreRelease);
            bool p2HasPre = !string.IsNullOrEmpty(p2.PreRelease);

            if (p1HasPre && !p2HasPre) return -1;
            if (!p1HasPre && p2HasPre) return 1;
            if (p1HasPre && p2HasPre)
            {
                return string.Compare(p1.PreRelease, p2.PreRelease, StringComparison.OrdinalIgnoreCase);
            }

            return 0;
        }

        /// <summary>
        /// Validates if a given version string is secure and authorized to submit earnings to the database.
        /// Returns false for revoked versions (e.g. 7.0.0-alpha) or versions below MinSecureVersion.
        /// </summary>
        public static bool IsVersionSecure(string? version)
        {
            if (string.IsNullOrWhiteSpace(version)) return false;
            string clean = version.Trim().TrimStart('v', 'V');
            if (DynamicRevokedVersions.Contains(clean))
                return false;
            foreach (var rev in RevokedVersions)
            {
                if (string.Equals(clean, rev.TrimStart('v', 'V'), StringComparison.OrdinalIgnoreCase))
                    return false;
            }
            return CompareSemVer(clean, DynamicMinSecureVersion) >= 0;
        }

        private static (Version Core, string PreRelease) ParseVersionCore(string v)
        {
            if (string.IsNullOrWhiteSpace(v))
                return (new Version(0, 0, 0), "");

            string clean = v.TrimStart('v', 'V').Trim();
            string pre = "";
            int dashIdx = clean.IndexOf('-');
            if (dashIdx >= 0)
            {
                pre = clean.Substring(dashIdx + 1);
                clean = clean.Substring(0, dashIdx);
            }

            string[] parts = clean.Split('.');
            int major = parts.Length > 0 && int.TryParse(parts[0], out int mj) ? mj : 0;
            int minor = parts.Length > 1 && int.TryParse(parts[1], out int mn) ? mn : 0;
            int patch = parts.Length > 2 && int.TryParse(parts[2], out int pt) ? pt : 0;

            return (new Version(major, minor, patch), pre);
        }
    }
}
