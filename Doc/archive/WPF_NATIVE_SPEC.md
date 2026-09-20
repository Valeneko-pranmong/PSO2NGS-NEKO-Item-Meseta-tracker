# 🗄️ NEKO Item & Meseta Tracker — Legacy C# WPF Native Tracker Specification

> **สถานะ:** `[ARCHIVED]` 🔴 — เอกสารสเปคที่ปลดระวางแล้ว (Historical Architecture Reference)  
> **วันที่ปลดระวาง:** 2026-09  
> **เอกสารที่ใช้งานจริงในปัจจุบัน (Active Source of Truth):** [`Doc/current/ACTIVE_SPECIFICATION.md`](../current/ACTIVE_SPECIFICATION.md)

---

## 1. ภาพรวมสถาปัตยกรรมเดิม (Former Architecture)

โปรเจกต์เนทีฟ Windows C# .NET 6 WPF (`NekoTracker-WPF/`) เคยถูกพัฒนาขึ้นเพื่อทดลองสร้างแอปพลิเคชันที่มีการเรนเดอร์กราฟิกด้วยฮาร์ดแวร์เร่งความเร็ว และมีระบบ AntiTamperGuard ตรวจจับการโกงในระดับ Process

### ส่วนประกอบที่สำคัญในอดีต:
* **UI Windows:** `MainWindow.xaml`, `OverlayWindow.xaml`
* **Log Pipeline:** `ActionLogParser.cs`, `LogWatcher.cs`
* **Security Subsystem:** `AntiTamperGuard.cs`, `IProcessValidator.cs`, `TamperViolation.cs`
* **Localization:** `LanguageManager.cs` (en, ja, th)
* **Unit Tests:** `NekoTracker.Tests` (AntiTamper, Localization, LogParser, Versioning)

---

## 2. เหตุผลในการยกเลิกและปลดระวาง (Retirement Rationale)

1. **การรวมศูนย์การพัฒนา (Consolidation to Python):** มุ่งเน้นการพัฒนาโปรแกรมหลักภาษา Python (`meseta_tracker.py`, `dashboard_ui.py`, `overlay_ui.py`, `modules/war_mode/`) ให้มีประสิทธิภาพและความคล่องตัวสูงสุด
2. **ลดความซ้ำซ้อนของโค้ดเบส (Codebase Simplification):** การดูแล 2 ภาษาควบคู่กันทำให้เกิดความซ้ำซ้อนในการอัปเดตนโยบาย Wire Contract, พิกัด Sector, และฟีเจอร์ War Room
3. **การเก็บรักษาประวัติ:** ซอร์สโค้ดทั้งหมดถูกย้ายไปยัง `archive/legacy_wpf/` เพื่อใช้ในการศึกษาหรืออ้างอิงย้อนหลัง
