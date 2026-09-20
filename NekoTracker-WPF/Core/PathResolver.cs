using System;
using System.IO;

namespace NekoTracker.Core
{
    public static class PathResolver
    {
        private static readonly string[] PossibleSubPaths = new[]
        {
            @"SEGA\PHANTASYSTARONLINE2\log_ngs",
            @"SEGA\PHANTASYSTARONLINE2_NA\log_ngs",
            @"SEGA\PHANTASYSTARONLINE2\log",
            @"SEGA\PHANTASYSTARONLINE2_NA\log"
        };

        public static string DetectDefaultLogFolder()
        {
            // 1. Standard MyDocuments
            string myDocs = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments);
            foreach (var sub in PossibleSubPaths)
            {
                string candidate = Path.Combine(myDocs, sub);
                if (Directory.Exists(candidate))
                    return candidate;
            }

            // 2. Check OneDrive Documents if user has OneDrive backup enabled
            string userProfile = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            string oneDriveDocs = Path.Combine(userProfile, "OneDrive", "Documents");
            if (Directory.Exists(oneDriveDocs))
            {
                foreach (var sub in PossibleSubPaths)
                {
                    string candidate = Path.Combine(oneDriveDocs, sub);
                    if (Directory.Exists(candidate))
                        return candidate;
                }
            }

            return string.Empty;
        }

        public static string? FindLatestLogFile(string folderPath)
        {
            if (string.IsNullOrWhiteSpace(folderPath) || !Directory.Exists(folderPath))
                return null;

            try
            {
                var dir = new DirectoryInfo(folderPath);
                var files = dir.GetFiles("ActionLog*.txt");
                if (files.Length == 0) return null;

                FileInfo? latest = null;
                foreach (var file in files)
                {
                    if (latest == null || file.LastWriteTime > latest.LastWriteTime)
                    {
                        latest = file;
                    }
                }

                return latest?.FullName;
            }
            catch
            {
                return null;
            }
        }
    }
}
