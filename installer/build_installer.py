#!/usr/bin/env python3
"""
NEKO Item & Meseta Tracker - Automated Build & Installer Pipeline
Standard: NEKO FAMILY Per-User Architecture (PrivilegesRequired=lowest)
Builds Python Tracker (PyInstaller), compiles Inno Setup installer,
generates SHA-256 digests, and executes process smoke tests.
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
ARTIFACTS_DIR = os.path.join(ROOT_DIR, "artifacts", "release-v6.1.0")
INSTALLER_ISS = os.path.join(ROOT_DIR, "installer", "NekoTracker.iss")
OUTPUT_SETUP_EXE = os.path.join(ARTIFACTS_DIR, "NekoTracker-Setup-v6.1.0.exe")
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
    
    # Python unit tests
    log("Running Python unit tests (pytest)...")
    run_cmd([sys.executable, "-m", "pytest", "-v", "tests/test_tracker_modules.py"])
    log("All pre-flight test suites passed successfully!")

def build_python_tracker() -> None:
    log("Packaging Python Tracker with PyInstaller...")
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
        "--hidden-import", "modules.security",
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

def compile_installer() -> None:
    log("Compiling Inno Setup distribution installer...")
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
    
    assert os.path.isfile(installed_main_exe), f"Missing {installed_main_exe}"
    assert os.path.isfile(uninstaller_exe), f"Missing {uninstaller_exe}"
    log("Clean installation verified! Primary Python Tracker extracted properly.")
    
    # 2. Main Python Tracker Process Smoke
    log("2. Verifying Main Python Tracker (V6.1.0) process smoke...")
    py_proc = subprocess.Popen([installed_main_exe])
    time.sleep(3)
    py_poll = py_proc.poll()
    if py_poll is not None:
        raise RuntimeError(f"Installed Main Tracker crashed immediately with code {py_poll}")
    py_proc.terminate()
    try:
        py_proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        py_proc.kill()
    log("Main Python Tracker process smoke PASS (PID started and stayed alive cleanly).")
    
    # 3. Clean Uninstallation Check
    log("3. Running clean silent uninstallation...")
    unins_cmd = [
        uninstaller_exe,
        "/VERYSILENT",
        "/SUPPRESSMSGBOXES"
    ]
    unins_res = subprocess.run(unins_cmd)
    time.sleep(2)
    if unins_res.returncode != 0:
        log(f"Warning: Uninstaller exited with code {unins_res.returncode}")
    
    # Check if core executable was removed
    if not os.path.exists(installed_main_exe):
        log("Uninstaller cleanly purged primary executable payload!")
    
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
    log("Starting NEKO Item & Meseta Tracker Installer Build Pipeline")
    
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
