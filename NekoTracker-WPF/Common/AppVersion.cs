using System;
using System.Reflection;

namespace NekoTracker.Common
{
    /// <summary>
    /// Centralized application versioning system for NEKO Tracker.
    /// Dynamically reflects assembly metadata defined in project properties.
    /// </summary>
    public static class AppVersion
    {
        public const string Channel = "Alpha";
        public const string DefaultVersion = "7.0.0-alpha";

        private static readonly Version _assemblyVersion;
        private static readonly string _informationalVersion;

        static AppVersion()
        {
            var assembly = Assembly.GetExecutingAssembly();
            _assemblyVersion = assembly.GetName().Version ?? new Version(7, 0, 0, 0);

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
