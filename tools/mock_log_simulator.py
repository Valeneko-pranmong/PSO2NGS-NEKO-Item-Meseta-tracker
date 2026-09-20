#!/usr/bin/env python3
"""
NEKO Item & Meseta Tracker - ActionLog Mock & Testing Simulator
Standard: PSO2:NGS ActionLog format (Tab-delimited)
Generates realistic ActionLog data for testing NekoTracker without needing PSO2:NGS running.
"""

import os
import sys
import time
import random
import argparse
from datetime import datetime

SAMPLE_ITEMS = [
    ("C/Astraea II", 1, 3),
    ("C/Gigas Maste", 1, 2),
    ("C/Gladia Soul", 1, 2),
    ("Arms Refiner II", 1, 1),
    ("N-Ex-Cube", 1, 5),
    ("N-Color Change Pass", 1, 1),
    ("Photon Chunk II A", 2, 8),
    ("Photon Chunk II B", 2, 8),
    ("C/Halphinale", 1, 1),
    ("Gold Primm Sword II", 1, 2),
]

def get_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

def generate_log_line(seq: int, action: str, player_id: str, char_name: str, payload: str) -> str:
    return f"{get_timestamp()}\t{seq}\t[{action}]\t{player_id}\t{char_name}\t{payload}\n"

class MockLogSimulator:
    def __init__(self, target_dir: str, player_id: str = "14743890", char_name: str = "Vale3neko", initial_wallet: int = 50_000_000):
        self.target_dir = os.path.abspath(target_dir)
        os.makedirs(self.target_dir, exist_ok=True)
        self.player_id = player_id
        self.char_name = char_name
        self.wallet = initial_wallet
        self.seq = 100
        
        # Name the file ActionLog<YYYYMMDD_HH>.txt matching NGS pattern
        today_str = datetime.now().strftime("%Y%m%d_%H")
        self.log_file = os.path.join(self.target_dir, f"ActionLog{today_str}.txt")

    def write_initial_seed(self) -> None:
        """Writes initial login and wallet balance entry."""
        with open(self.log_file, "a", encoding="utf-8") as f:
            # Login / First pickup line setting character and initial wallet
            line = generate_log_line(
                self.seq, "Pickup", self.player_id, self.char_name,
                f"N-Meseta(1000)\tCurrentN-Meseta({self.wallet})"
            )
            f.write(line)
            f.flush()
        print(f"[SIMULATOR] Initialized mock log at: {self.log_file}")
        print(f"[SIMULATOR] Operative: {self.char_name} (ID: {self.player_id})")
        print(f"[SIMULATOR] Starting Wallet: {self.wallet:,} N-Meseta")
        self.seq += 1

    def emit_meseta_drop(self, amount: int = None, action: str = "Pickup") -> int:
        if amount is None:
            # Random drop between 1,500 and 25,000 N-Meseta
            amount = random.choice([1500, 2500, 3200, 5000, 12000, 25000, 50000])
        self.wallet += amount
        self.seq += 1
        line = generate_log_line(
            self.seq, action, self.player_id, self.char_name,
            f"N-Meseta({amount})\tCurrentN-Meseta({self.wallet})"
        )
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
        print(f"[SIMULATOR] +{amount:,} N-Meseta ({action}) | Total Wallet: {self.wallet:,}")
        return amount

    def emit_item_drop(self, item_name: str = None, count: int = None) -> tuple:
        if not item_name:
            item_choice, min_c, max_c = random.choice(SAMPLE_ITEMS)
            item_name = item_choice
            count = random.randint(min_c, max_c)
        self.seq += 1
        line = generate_log_line(
            self.seq, "Pickup", self.player_id, self.char_name,
            f"{item_name}\tNum({count})"
        )
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
        print(f"[SIMULATOR] Drop: {item_name} x{count}")
        return item_name, count

    def emit_pse_burst(self) -> int:
        print("\n⚡ [SIMULATOR] >>> PSE BURST TRIGGERED! (Farming Frenzy) <<< ⚡")
        total = 0
        for _ in range(5):
            amt = random.randint(15_000, 45_000)
            self.emit_meseta_drop(amt, action="Pickup")
            total += amt
            time.sleep(0.4)
        
        # Climax Boss drop
        boss_amt = random.randint(80_000, 150_000)
        self.emit_meseta_drop(boss_amt, action="Reward")
        total += boss_amt
        
        # Rare item drop
        self.emit_item_drop("C/Gladia Soul", 2)
        print(f"⚡ [SIMULATOR] PSE Burst Complete: +{total:,} N-Meseta earned!\n")
        return total

    def run_stream(self, interval: float = 2.0, max_events: int = 0) -> None:
        self.write_initial_seed()
        print(f"[SIMULATOR] Streaming live ActionLog events every {interval}s (Press Ctrl+C to stop)...")
        count = 0
        try:
            while True:
                time.sleep(interval)
                dice = random.random()
                if dice < 0.15:
                    self.emit_pse_burst()
                elif dice < 0.50:
                    self.emit_item_drop()
                elif dice < 0.75:
                    self.emit_meseta_drop(action="Pickup")
                else:
                    self.emit_meseta_drop(action="AutoSell")
                count += 1
                if max_events > 0 and count >= max_events:
                    print(f"[SIMULATOR] Finished emitting {count} events.")
                    break
        except KeyboardInterrupt:
            print("\n[SIMULATOR] Simulation stopped by user.")

    def generate_static(self, num_events: int = 50) -> None:
        """Generates static history in log file instantly."""
        self.write_initial_seed()
        print(f"[SIMULATOR] Generating {num_events} static ActionLog events...")
        for i in range(num_events):
            if i % 8 == 0:
                self.emit_item_drop()
            elif i % 5 == 0:
                self.emit_meseta_drop(action="AutoSell")
            else:
                self.emit_meseta_drop(action="Pickup")
        print(f"[SIMULATOR] Successfully wrote {num_events} events to {self.log_file}")

def main():
    parser = argparse.ArgumentParser(description="PSO2:NGS ActionLog Mock Simulator")
    parser.add_argument("--dir", default="test_logs", help="Target directory for mock log files (default: test_logs)")
    parser.add_argument("--stream", action="store_true", help="Continuously stream live events")
    parser.add_argument("--static", action="store_true", help="Generate static test log file and exit")
    parser.add_argument("--events", type=int, default=30, help="Number of events for static generation")
    parser.add_argument("--interval", type=float, default=2.5, help="Seconds between streaming events (default: 2.5)")
    parser.add_argument("--character", default="Vale3neko", help="Simulated in-game character name")
    parser.add_argument("--player-id", default="14743890", help="Simulated player ID")
    parser.add_argument("--wallet", type=int, default=50_000_000, help="Starting wallet N-Meseta")
    
    args = parser.parse_args()
    
    sim = MockLogSimulator(
        target_dir=args.dir,
        player_id=args.player_id,
        char_name=args.character,
        initial_wallet=args.wallet
    )
    
    if args.static:
        sim.generate_static(num_events=args.events)
    else:
        # Default is streaming mode
        sim.run_stream(interval=args.interval)

if __name__ == "__main__":
    main()
