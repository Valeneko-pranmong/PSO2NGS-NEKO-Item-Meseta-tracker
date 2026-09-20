using System;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Threading;
using Microsoft.Win32;
using NekoTracker.Common;
using NekoTracker.Core;
using NekoTracker.Localization;
using NekoTracker.Security;

namespace NekoTracker
{
    public partial class MainWindow : Window
    {
        private readonly TrackerStats _stats;
        private readonly AntiTamperGuard _antiTamper;
        private readonly LogWatcher _watcher;
        private readonly DispatcherTimer _uiTimer;
        private OverlayWindow? _overlayWindow;

        public MainWindow()
        {
            InitializeComponent();

            _stats = new TrackerStats();
            _antiTamper = new AntiTamperGuard();
            _watcher = new LogWatcher(_stats, _antiTamper);

            // Version tags
            TxtVersionTag.Text = AppVersion.DisplayVersion;
            TxtFooterVersion.Text = AppVersion.DisplayVersion;

            // UI Refresh Timer
            _uiTimer = new DispatcherTimer
            {
                Interval = TimeSpan.FromSeconds(1)
            };
            _uiTimer.Tick += (s, e) => UpdateLiveStats();
            _uiTimer.Start();

            // Event bindings
            _stats.OnStatsUpdated += () => Dispatcher.InvokeAsync(UpdateUI);
            _antiTamper.OnViolation += _ => Dispatcher.InvokeAsync(UpdateSecurityBadge);
            _watcher.OnLogFileChanged += path => Dispatcher.InvokeAsync(() =>
            {
                TxtLogFolderStatus.Text = $"Active: {Path.GetFileName(path)}";
            });

            LanguageManager.Instance.OnLanguageChanged += _ => Dispatcher.InvokeAsync(ApplyLocalization);

            ApplyLocalization();
            AutoDetectAndStartLogWatcher();
            UpdateUI();
        }

        private void Window_MouseDown(object sender, MouseButtonEventArgs e)
        {
            if (e.ChangedButton == MouseButton.Left)
            {
                this.DragMove();
            }
        }

        private void AutoDetectAndStartLogWatcher()
        {
            string detected = PathResolver.DetectDefaultLogFolder();
            if (!string.IsNullOrEmpty(detected))
            {
                _watcher.SetLogFolder(detected);
                TxtLogFolderStatus.Text = $"Detected: {detected}";
            }
            else
            {
                TxtLogFolderStatus.Text = LanguageManager.Instance["LogStatusWaiting"];
            }
        }

        private void ApplyLocalization()
        {
            var lm = LanguageManager.Instance;
            TxtAppTitle.Text = lm["AppTitle"];
            BtnSelectFolder.Content = $"📂 {lm["SelectLogFolder"]}";
            BtnOverlay.Content = $"📱 {lm["GadgetMode"]}";
            BtnReset.Content = $"🔄 {lm["ResetSession"]}";

            LblIncome.Text = lm["SessionIncome"].ToUpperInvariant();
            LblRate.Text = lm["MesetaPerHour"].ToUpperInvariant();
            LblWallet.Text = lm["CurrentWallet"].ToUpperInvariant();
            LblDuration.Text = lm["FarmingDuration"].ToUpperInvariant();

            LblTotalDrops.Text = lm["TotalDrops"];
            ChkWatchlistOnly.Content = lm["WatchlistFilter"];

            UpdateSecurityBadge();
            UpdateLanguageButtonHighlights();
        }

        private void UpdateLanguageButtonHighlights()
        {
            string cur = LanguageManager.Instance.CurrentLanguage;
            BtnLangEn.Background = cur == LanguageManager.LangEn ? (Brush)FindResource("BrushPinkAccent") : Brushes.Transparent;
            BtnLangEn.Foreground = cur == LanguageManager.LangEn ? Brushes.White : (Brush)FindResource("BrushTextMain");

            BtnLangTh.Background = cur == LanguageManager.LangTh ? (Brush)FindResource("BrushPinkAccent") : Brushes.Transparent;
            BtnLangTh.Foreground = cur == LanguageManager.LangTh ? Brushes.White : (Brush)FindResource("BrushTextMain");

            BtnLangJa.Background = cur == LanguageManager.LangJa ? (Brush)FindResource("BrushPinkAccent") : Brushes.Transparent;
            BtnLangJa.Foreground = cur == LanguageManager.LangJa ? Brushes.White : (Brush)FindResource("BrushTextMain");
        }

        private void UpdateLiveStats()
        {
            TxtDurationVal.Text = TrackerStats.FormatDuration(_stats.GetDuration());
            TxtRateVal.Text = TrackerStats.FormatRate(_stats.GetMesetaPerHour());
        }

        private void UpdateUI()
        {
            TxtIncomeVal.Text = TrackerStats.FormatCompact(_stats.SessionMeseta);
            TxtWalletVal.Text = TrackerStats.FormatCompact(_stats.CurrentWallet);
            UpdateLiveStats();

            if (!string.IsNullOrEmpty(_stats.CharacterName))
            {
                TxtCharacterInfo.Text = $"Operative: {_stats.CharacterName} ({_stats.PlayerId})";
            }

            LstDrops.ItemsSource = _stats.GetFilteredItems(TxtSearchBox.Text);
            UpdateSecurityBadge();
        }

        private void UpdateSecurityBadge()
        {
            var lm = LanguageManager.Instance;
            if (_antiTamper.IsCompromised)
            {
                MainSecurityBorder.Background = new SolidColorBrush(Color.FromRgb(255, 235, 238));
                TxtMainSecurityIcon.Text = "⚠️";
                TxtMainSecurityText.Text = lm["AntiTamperCompromised"];
                TxtMainSecurityText.Foreground = (Brush)FindResource("BrushRedWarning");
            }
            else
            {
                MainSecurityBorder.Background = new SolidColorBrush(Color.FromRgb(232, 245, 233));
                TxtMainSecurityIcon.Text = "🛡️";
                TxtMainSecurityText.Text = lm["AntiTamperSecure"];
                TxtMainSecurityText.Foreground = (Brush)FindResource("BrushGreenSafe");
            }
        }

        private void BtnLang_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button btn)
            {
                string tag = btn.Content.ToString()?.ToLowerInvariant() ?? "en";
                LanguageManager.Instance.CurrentLanguage = tag;
            }
        }

        private void BtnSelectFolder_Click(object sender, RoutedEventArgs e)
        {
            // Standard Windows Folder Selection using modern dialog or OpenFileDialog trick
            var dialog = new OpenFileDialog
            {
                ValidateNames = false,
                CheckFileExists = false,
                CheckPathExists = true,
                FileName = "Select Folder",
                Title = LanguageManager.Instance["SelectLogFolder"]
            };

            if (dialog.ShowDialog() == true)
            {
                string? folder = Path.GetDirectoryName(dialog.FileName);
                if (!string.IsNullOrEmpty(folder) && Directory.Exists(folder))
                {
                    _watcher.SetLogFolder(folder);
                    TxtLogFolderStatus.Text = $"Folder: {folder}";
                }
            }
        }

        private void BtnOverlay_Click(object sender, RoutedEventArgs e)
        {
            if (_overlayWindow == null || !_overlayWindow.IsLoaded)
            {
                _overlayWindow = new OverlayWindow(_stats, _antiTamper);
                _overlayWindow.OnRequestMainWindow += () =>
                {
                    this.Show();
                    this.WindowState = WindowState.Normal;
                    this.Activate();
                };
            }

            _overlayWindow.Show();
            _overlayWindow.Activate();
        }

        private void BtnReset_Click(object sender, RoutedEventArgs e)
        {
            _stats.Reset();
            _antiTamper.Reset();
            UpdateUI();
        }

        private void ChkWatchlistOnly_Changed(object sender, RoutedEventArgs e)
        {
            _stats.IsWatchlistOnly = ChkWatchlistOnly.IsChecked == true;
            LstDrops.ItemsSource = _stats.GetFilteredItems(TxtSearchBox.Text);
        }

        private void TxtSearchBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            LstDrops.ItemsSource = _stats.GetFilteredItems(TxtSearchBox.Text);
        }

        private void BtnMinimize_Click(object sender, RoutedEventArgs e)
        {
            this.WindowState = WindowState.Minimized;
        }

        private void BtnClose_Click(object sender, RoutedEventArgs e)
        {
            _watcher.Dispose();
            _overlayWindow?.Close();
            Application.Current.Shutdown();
        }
    }
}
