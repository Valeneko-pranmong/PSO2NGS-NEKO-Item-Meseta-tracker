using System;
using System.Diagnostics;
using System.Linq;

namespace NekoTracker.Security
{
    public interface IProcessValidator
    {
        bool IsGameProcessRunning();
    }

    public class WindowsProcessValidator : IProcessValidator
    {
        private static readonly string[] KnownPso2ProcessNames = new[]
        {
            "pso2",
            "pso2ngs",
            "pso2bin",
            "pso2_bin"
        };

        public bool IsGameProcessRunning()
        {
            try
            {
                var processes = Process.GetProcesses();
                return processes.Any(p =>
                {
                    try
                    {
                        return KnownPso2ProcessNames.Contains(p.ProcessName.ToLowerInvariant());
                    }
                    catch
                    {
                        return false;
                    }
                });
            }
            catch
            {
                // In case process enumeration is blocked, fallback to permissive to avoid false positives
                return true;
            }
        }
    }
}
