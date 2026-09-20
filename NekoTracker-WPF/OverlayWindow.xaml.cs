using System;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Threading;
using NekoTracker.Common;
using NekoTracker.Core;
using NekoTracker.Localization;
using NekoTracker.Security;

namespace NekoTracker
{
    public partial class OverlayWindow : Window
    {
        private readonly TrackerStats _stats;
        private readonly AntiTamperGuard _antiTamper;
        private readonly DispatcherTimer _uiTimer;
        private bool _isClickThrough = false;
        private bool _isHighOpacity = true;

        public event Action? OnRequestMainWindow;

        public OverlayWindow(TrackerStats stats, AntiTamperGuard antiTamper)
        {
            InitializeComponent();
            _stats = stats;
            _antiTamper = antiTamper;

            TxtVersionBadge.Text = AppVersion.DisplayVersion;

            _uiTimer = new DispatcherTimer
            {
                Interval = TimeSpan.FromSeconds(1)
            };
            _uiTimer.Tick += (s, e) => UpdateUI();
            _uiTimer.Start();

            _stats.OnStatsUpdated += () => Dispatcher.InvokeAsync(UpdateUI);
            _antiTamper.OnViolation += _ => Dispatcher.InvokeAsync(UpdateSecurityBadge);

            LanguageManager.Instance.OnLanguageChanged += _ => Dispatcher.InvokeAsync(ApplyLocalization);
            ApplyLocalization();
            UpdateUI();
        }

        private void Window_MouseDown(object sender, MouseButtonEventArgs e)
        {
            if (e.ChangedButton == MouseButton.Left)
            {
                this.DragMove();
            }
        }

        private void ApplyLocalization()
        {
            var lm = LanguageManager.Instance;
            TxtRateHeader.Text = lm["MesetaPerHour"].ToUpperInvariant();
            UpdateSecurityBadge();
        }

        public void UpdateUI()
        {
            TxtMesetaRate.Text = TrackerStats.FormatRate(_stats.GetMesetaPerHour());
            TxtSessionMeseta.Text = TrackerStats.FormatCompact(_stats.SessionMeseta);
            TxtDuration.Text = TrackerStats.FormatDuration(_stats.GetDuration());

            if (!string.IsNullOrEmpty(_stats.CharacterName))
            {
                TxtCharacterInfo.Text = $"{_stats.CharacterName}";
            }

            // Bind items
            ItemListControl.ItemsSource = _stats.GetFilteredItems();
            UpdateSecurityBadge();
        }

        private void UpdateSecurityBadge()
        {
            var lm = LanguageManager.Instance;
            if (_antiTamper.IsCompromised)
            {
                SecurityBorder.Background = new SolidColorBrush(Color.FromRgb(255, 235, 238));
                TxtSecurityIcon.Text = "⚠️";
                TxtSecurityText.Text = lm["AntiTamperCompromised"];
                TxtSecurityText.Foreground = (Brush)FindResource("BrushRedWarning");
            }
            else
            {
                SecurityBorder.Background = new SolidColorBrush(Color.FromRgb(232, 245, 233));
                TxtSecurityIcon.Text = "🛡️";
                TxtSecurityText.Text = lm["AntiTamperSecure"];
                TxtSecurityText.Foreground = (Brush)FindResource("BrushGreenSafe");
            }
        }

        private void BtnOpacity_Click(object sender, RoutedEventArgs e)
        {
            _isHighOpacity = !_isHighOpacity;
            RootBorder.Opacity = _isHighOpacity ? 0.95 : 0.60;
        }

        private void BtnClickThrough_Click(object sender, RoutedEventArgs e)
        {
            _isClickThrough = !_isClickThrough;
            NativeMethods.SetClickThrough(this, _isClickThrough);
            BtnClickThrough.Background = _isClickThrough
                ? (Brush)FindResource("BrushPinkAccent")
                : (Brush)FindResource("BrushPinkHeader");
        }

        private void BtnReturnMain_Click(object sender, RoutedEventArgs e)
        {
            OnRequestMainWindow?.Invoke();
            this.Hide();
        }

        private void BtnClose_Click(object sender, RoutedEventArgs e)
        {
            this.Hide();
        }
    }
}
