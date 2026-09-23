#!/usr/bin/env python3
"""
NEKO Item & Meseta Tracker - Automated Build & Installer Pipeline
Standard: NEKO FAMILY Per-User Architecture (PrivilegesRequired=lowest)
Target Version: 7.1.0 (Modular Python Engine with ARKS War Room, i18n & Test Suite)
Builds Python Tracker, compiles NekoLogSimulator, compiles Inno Setup installer,
generates SHA-256 digests, and executes complete lifecycle process smoke tests.
"""

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import time

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BUILD_DIR = os.path.join(ROOT_DIR, "build")
DIST_DIR = os.path.join(ROOT_DIR, "dist")
ARTIFACTS_DIR = os.path.join(ROOT_DIR, "artifacts", "release-v7.1.0")
INSTALLER_ISS = os.path.join(ROOT_DIR, "installer", "NekoTracker.iss")
OUTPUT_SETUP_EXE = os.path.join(ARTIFACTS_DIR, "NekoTracker-Setup-v7.1.0.exe")
SHA256_FILE = os.path.join(ARTIFACTS_DIR, "SHA256SUMS.txt")

def log(msg: str) -> None:
    print(f"\n[NEKO-BUILD] >>> {msg}", flush=True)

def find_iscc() -> str:
    """Locate Inno Setup Command-Line Compiler (ISCC.exe)."""
    candidates = [
        shutil.which("iscc"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"),
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Inno Setup 7\ISCC.exe"),
        r"C:\Program Files (x86)\Inno Setup 7\ISCC.exe",
        r"C:\Program Files\Inno Setup 7\ISCC.exe",
    ]
    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            return candidate
    raise FileNotFoundError("ISCC.exe (Inno Setup 6) could not be located on this machine.")

def run_cmd(cmd: list, cwd: str = ROOT_DIR, check: bool = True) -> subprocess.CompletedProcess:
    log(f"Executing: {' '.join(cmd)} (in {cwd})")
    res = subprocess.run(cmd, cwd=cwd)
    if check and res.returncode != 0:
        print(f"[NEKO-BUILD] ERROR: Command failed with exit code {res.returncode}", file=sys.stderr)
        sys.exit(res.returncode)
    return res

def run_test_suites() -> None:
    log("Running pre-flight automated test suites...")
    log("Running all unit and integration test suites (pytest tests/)...")
    run_cmd([sys.executable, "-m", "pytest", "-v", "tests/"])
    log("All pre-flight test suites passed successfully!")

def build_python_tracker() -> None:
    log("Packaging Python Tracker (V7.1.0) with PyInstaller...")
    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "NekoTracker",
        "--icon", "icon.ico",
        "--add-data", "logo.png;.",
        "--add-data", "icon.ico;.",
        "--add-data", "fonts;fonts",
        "--collect-all", "customtkinter",
        "--collect-all", "modules",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "modules.event_bus",
        "--hidden-import", "modules.i18n",
        "--hidden-import", "modules.guide_dialog",
        "--hidden-import", "modules.utils",
        "--hidden-import", "modules.version",
        "--hidden-import", "modules.security",
        "--hidden-import", "modules.anti_tamper",
        "--hidden-import", "modules.war_mode.war_service",
        "--hidden-import", "modules.war_mode.war_view",
        "--hidden-import", "tools.firebase_war_sync",
        "meseta_tracker.py"
    ]
    run_cmd(pyinstaller_cmd)
    
    out_exe = os.path.join(DIST_DIR, "NekoTracker", "NekoTracker.exe")
    if not os.path.isfile(out_exe):
        raise RuntimeError(f"PyInstaller failed to create {out_exe}")
    log(f"Python Tracker build completed: {out_exe}")

def build_mock_simulator() -> None:
    log("Packaging NekoLogSimulator standalone executable for test machines...")
    sim_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--console",
        "--name", "NekoLogSimulator",
        "--icon", "icon.ico",
        os.path.join(ROOT_DIR, "tools", "mock_log_simulator.py")
    ]
    run_cmd(sim_cmd)
    
    # Remove leftover spec if created
    leftover_spec = os.path.join(ROOT_DIR, "NekoLogSimulator.spec")
    if os.path.exists(leftover_spec):
        try:
            os.remove(leftover_spec)
        except OSError:
            pass

    out_sim_exe = os.path.join(DIST_DIR, "NekoLogSimulator.exe")
    if not os.path.isfile(out_sim_exe):
        raise RuntimeError(f"PyInstaller failed to create {out_sim_exe}")
    log(f"NekoLogSimulator build completed: {out_sim_exe}")

def compile_installer() -> None:
    log("Compiling Inno Setup distribution installer (V7.1.0)...")
    iscc_path = find_iscc()
    log(f"Using Inno Setup compiler: {iscc_path}")
    
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    run_cmd([iscc_path, INSTALLER_ISS], cwd=os.path.join(ROOT_DIR, "installer"))
    
    if not os.path.isfile(OUTPUT_SETUP_EXE):
        raise RuntimeError(f"Inno Setup failed to create {OUTPUT_SETUP_EXE}")
    
    size_mb = os.path.getsize(OUTPUT_SETUP_EXE) / (1024 * 1024)
    log(f"Installer compiled successfully: {OUTPUT_SETUP_EXE} ({size_mb:.2f} MB)")

def compute_checksums() -> str:
    log("Generating authoritative SHA-256 digests...")
    sha = hashlib.sha256()
    with open(OUTPUT_SETUP_EXE, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    digest = sha.hexdigest()
    
    line = f"{digest}  {os.path.basename(OUTPUT_SETUP_EXE)}\n"
    with open(SHA256_FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write(line)
    
    log(f"SHA256: {digest}")
    log(f"Saved to: {SHA256_FILE}")

    # Synchronize SHA-256 digest atomically across release documentation & QA checklists
    import re
    doc_sync_targets = [
        (os.path.join(ARTIFACTS_DIR, "E2E_TEST_CHECKLIST.md"), r"`[0-9a-fA-F]{64}`"),
        (os.path.join(ROOT_DIR, "Doc", "current", "E2E_TEST_GUIDE.md"), r"`[0-9a-fA-F]{64}`"),
        (os.path.join(ARTIFACTS_DIR, "README.md"), r"[0-9a-fA-F]{64}(?=\s+NekoTracker-Setup-v7\.1\.0\.exe)"),
        (os.path.join(ROOT_DIR, "Doc", "current", "ENGINEERING_LOG.md"), r"(?<=NekoTracker-Setup-v7\.1\.0\.exe`: `)[0-9a-fA-F]{64}"),
    ]
    for path, pattern in doc_sync_targets:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as df:
                content = df.read()
            if "`" in pattern:
                new_content = re.sub(pattern, f"`{digest}`", content)
            else:
                new_content = re.sub(pattern, digest, content)
            if new_content != content:
                with open(path, "w", encoding="utf-8", newline="\n") as df:
                    df.write(new_content)
                log(f"Synchronized SHA-256 hash in {os.path.relpath(path, ROOT_DIR)}")

    return digest

def smoke_test_installer() -> None:
    log("Executing automated installer lifecycle & process smoke test...")
    sandbox_dir = os.path.join(BUILD_DIR, "smoke_sandbox")
    if os.path.exists(sandbox_dir):
        shutil.rmtree(sandbox_dir, ignore_errors=True)
    os.makedirs(sandbox_dir, exist_ok=True)
    
    # 1. Clean installation check (Per-user non-elevated sandbox)
    log(f"1. Installing into sandbox: {sandbox_dir} ...")
    install_cmd = [
        OUTPUT_SETUP_EXE,
        "/VERYSILENT",
        "/SUPPRESSMSGBOXES",
        f"/DIR={sandbox_dir}"
    ]
    res = subprocess.run(install_cmd)
    if res.returncode != 0:
        raise RuntimeError(f"Installer failed with returncode {res.returncode}")
    
    installed_main_exe = os.path.join(sandbox_dir, "NekoTracker.exe")
    uninstaller_exe = os.path.join(sandbox_dir, "unins000.exe")
    uninstall_bat = os.path.join(sandbox_dir, "Uninstall.bat")
    how_to_use_file = os.path.join(sandbox_dir, "HOW_TO_USE.md")
    
    assert os.path.isfile(installed_main_exe), f"Missing {installed_main_exe}"
    assert os.path.isfile(uninstaller_exe), f"Missing {uninstaller_exe}"
    assert os.path.isfile(uninstall_bat), f"Missing {uninstall_bat}"
    assert os.path.isfile(how_to_use_file), f"Missing {how_to_use_file}"

    # Strict Production E2E Check: Ensure ZERO test/mock artifacts leaked into installer
    assert not os.path.exists(os.path.join(sandbox_dir, "tools")), "Test simulator leaked into production installer!"
    assert not os.path.exists(os.path.join(sandbox_dir, "sample_logs")), "Sample logs leaked into production installer!"
    assert not os.path.exists(os.path.join(sandbox_dir, "Quick_Test_All_In_One.bat")), "Test runner leaked into production installer!"
    assert not os.path.exists(os.path.join(sandbox_dir, "Run_Test_Mode.bat")), "Test runner leaked into production installer!"
    assert not os.path.exists(os.path.join(sandbox_dir, "Start_Mock_Stream.bat")), "Test streamer leaked into production installer!"
    log("Production E2E installation verified! Only genuine application payload & uninstaller extracted.")
    
    # 2. Main Python Tracker Process Smoke
    log("2. Verifying Main Python Tracker (V7.1.0) process smoke...")
    py_proc = subprocess.Popen([installed_main_exe])
    pid = py_proc.pid
    log(f"Child process launched (PID: {pid}). Polling readiness across stabilization window...")

    # Bounded readiness polling: verify process stays alive and healthy without blind sleep
    readiness_deadline = time.time() + 6.0
    stable_samples = 0
    poll_interval = 0.25

    while time.time() < readiness_deadline:
        poll_code = py_proc.poll()
        if poll_code is not None:
            raise RuntimeError(f"Installed Main Tracker (PID {pid}) crashed immediately with code {poll_code}")
        stable_samples += 1
        time.sleep(poll_interval)

    # Clean termination bound strictly to exact child handle / PID
    log(f"Process stability verified over {stable_samples} samples ({time.time() - (readiness_deadline - 6.0):.2f}s). Terminating PID {pid}...")
    py_proc.terminate()
    try:
        py_proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        log(f"Graceful terminate timed out for PID {pid}, sending kill signal...")
        py_proc.kill()
        py_proc.wait(timeout=3)
    log(f"Main Python Tracker process smoke PASS (exact child PID {pid} started, remained stable, and terminated cleanly).")

    # 3. Clean Uninstallation Check
    log("3. Running clean silent uninstallation...")
    unins_cmd = [
        uninstaller_exe,
        "/VERYSILENT",
        "/SUPPRESSMSGBOXES"
    ]
    unins_res = subprocess.run(unins_cmd)
    if unins_res.returncode != 0:
        log(f"Warning: Uninstaller exited with code {unins_res.returncode}")

    # Bounded poll for uninstallation purge completion
    unins_deadline = time.time() + 10.0
    while time.time() < unins_deadline:
        if not os.path.exists(installed_main_exe) and not os.path.exists(uninstaller_exe):
            break
        time.sleep(0.5)

    if not os.path.exists(installed_main_exe):
        log("Uninstaller cleanly purged primary executable payload!")
    else:
        raise RuntimeError(f"Uninstaller failed to remove primary executable: {installed_main_exe}")

    if not os.path.exists(uninstaller_exe):
        log("Uninstaller cleanly purged uninstaller binary!")
    
    # Cleanup remaining sandbox
    shutil.rmtree(sandbox_dir, ignore_errors=True)
    log("Installer lifecycle smoke test fully PASSED!")

def main() -> None:
    parser = argparse.ArgumentParser(description="NEKO Tracker Installer Builder")
    parser.add_argument("--skip-tests", action="store_true", help="Skip pre-flight test suites")
    parser.add_argument("--skip-build", action="store_true", help="Skip compiling binaries")
    parser.add_argument("--skip-smoke", action="store_true", help="Skip installer smoke test")
    args = parser.parse_args()
    
    start_time = time.time()
    log("Starting NEKO Item & Meseta Tracker Installer Build Pipeline (V7.1.0)")
    
    if not args.skip_tests:
        run_test_suites()
    
    if not args.skip_build:
        build_python_tracker()
        
    compile_installer()
    digest = compute_checksums()
    
    if not args.skip_smoke:
        smoke_test_installer()
    
    elapsed = time.time() - start_time
    size_mb = os.path.getsize(OUTPUT_SETUP_EXE) / (1024 * 1024)
    
    print("\n" + "="*70)
    print(" 🌸 NEKO ITEM & MESETA TRACKER - BUILD SUCCESSFUL")
    print("="*70)
    print(f" Artifact: {OUTPUT_SETUP_EXE}")
    print(f" Size:     {size_mb:.2f} MB")
    print(f" SHA-256:  {digest}")
    print(f" Duration: {elapsed:.2f} seconds")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
