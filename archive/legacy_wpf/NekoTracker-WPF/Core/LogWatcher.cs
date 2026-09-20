using System;
using System.IO;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using NekoTracker.Security;

namespace NekoTracker.Core
{
    public class LogWatcher : IDisposable
    {
        private FileSystemWatcher? _fileWatcher;
        private readonly TrackerStats _stats;
        private readonly AntiTamperGuard _antiTamper;
        private readonly Timer _fallbackPollTimer;

        private string _logFolder = string.Empty;
        private string? _currentLogFile = null;
        private long _lastFilePosition = 0;
        private Encoding _encoding = Encoding.Unicode; // Default UTF-16 LE

        private readonly object _syncRoot = new();
        private bool _isReading = false;

        public event Action<string>? OnLogFileChanged;
        public event Action<string>? OnError;

        public string LogFolder => _logFolder;
        public string? CurrentLogFile => _currentLogFile;
        public bool IsActive => !string.IsNullOrEmpty(_logFolder) && Directory.Exists(_logFolder);

        public LogWatcher(TrackerStats stats, AntiTamperGuard antiTamper)
        {
            _stats = stats;
            _antiTamper = antiTamper;

            // 1-second fallback poll timer in case FileSystemWatcher events are delayed
            _fallbackPollTimer = new Timer(_ => ReadPendingLogLines(), null, Timeout.Infinite, Timeout.Infinite);
        }

        public void SetLogFolder(string folderPath)
        {
            lock (_syncRoot)
            {
                if (string.IsNullOrWhiteSpace(folderPath) || !Directory.Exists(folderPath))
                    return;

                _logFolder = folderPath;
                _currentLogFile = null;
                _lastFilePosition = 0;

                _fileWatcher?.Dispose();
                _fileWatcher = new FileSystemWatcher(_logFolder, "ActionLog*.txt")
                {
                    NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.FileName | NotifyFilters.Size,
                    EnableRaisingEvents = true
                };

                _fileWatcher.Changed += (s, e) => ReadPendingLogLines();
                _fileWatcher.Created += (s, e) => SwitchToLatestFile();
                _fileWatcher.Renamed += (s, e) => SwitchToLatestFile();

                SwitchToLatestFile();
                _fallbackPollTimer.Change(1000, 1000);
            }
        }

        private void SwitchToLatestFile()
        {
            lock (_syncRoot)
            {
                string? latest = PathResolver.FindLatestLogFile(_logFolder);
                if (latest != null && latest != _currentLogFile)
                {
                    _currentLogFile = latest;
                    _lastFilePosition = 0;
                    DetectFileEncoding(_currentLogFile);
                    OnLogFileChanged?.Invoke(_currentLogFile);
                }
            }
            ReadPendingLogLines();
        }

        private void DetectFileEncoding(string filePath)
        {
            try
            {
                if (!File.Exists(filePath)) return;
                byte[] bom = new byte[4];
                using (var fs = new FileStream(filePath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
                {
                    int read = fs.Read(bom, 0, 4);
                    if (read >= 2 && bom[0] == 0xFF && bom[1] == 0xFE)
                        _encoding = Encoding.Unicode; // UTF-16 LE
                    else if (read >= 2 && bom[0] == 0xFE && bom[1] == 0xFF)
                        _encoding = Encoding.BigEndianUnicode; // UTF-16 BE
                    else if (read >= 3 && bom[0] == 0xEF && bom[1] == 0xBB && bom[2] == 0xBF)
                        _encoding = Encoding.UTF8; // UTF-8 with BOM
                    else
                        _encoding = Encoding.UTF8;
                }
            }
            catch
            {
                _encoding = Encoding.Unicode;
            }
        }

        public void ReadPendingLogLines()
        {
            if (string.IsNullOrEmpty(_currentLogFile) || !File.Exists(_currentLogFile))
            {
                SwitchToLatestFile();
                if (string.IsNullOrEmpty(_currentLogFile) || !File.Exists(_currentLogFile))
                    return;
            }

            lock (_syncRoot)
            {
                if (_isReading) return;
                _isReading = true;
            }

            try
            {
                var fileInfo = new FileInfo(_currentLogFile);
                long fileSize = fileInfo.Length;

                // Validate stream integrity through Anti-Tamper Guard
                if (!_antiTamper.ValidateStream(_lastFilePosition, fileSize))
                {
                    return;
                }

                if (fileSize < _lastFilePosition)
                {
                    // File truncated or rotated
                    _lastFilePosition = 0;
                }

                if (fileSize == _lastFilePosition)
                {
                    return; // No new bytes
                }

                using var fs = new FileStream(_currentLogFile, FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
                fs.Seek(_lastFilePosition, SeekOrigin.Begin);

                using var reader = new StreamReader(fs, _encoding, detectEncodingFromByteOrderMarks: false, bufferSize: 4096, leaveOpen: true);
                string? line;
                while ((line = reader.ReadLine()) != null)
                {
                    if (string.IsNullOrWhiteSpace(line)) continue;

                    var record = ActionLogParser.ParseLine(line);
                    if (record != null)
                    {
                        // Validate record through Anti-Tamper pipeline
                        if (_antiTamper.ValidateRecord(record))
                        {
                            _stats.ProcessRecord(record);
                        }
                    }
                }

                _lastFilePosition = fs.Position;
            }
            catch (Exception ex)
            {
                OnError?.Invoke(ex.Message);
            }
            finally
            {
                lock (_syncRoot)
                {
                    _isReading = false;
                }
            }
        }

        public void Dispose()
        {
            _fallbackPollTimer.Dispose();
            _fileWatcher?.Dispose();
        }
    }
}
