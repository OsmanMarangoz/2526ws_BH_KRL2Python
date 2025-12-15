#!/usr/bin/env python3
"""
Offline PTP Cartesian sequence runner (no robot connection).
- Lists available CSV files in project folder
- Lets user choose a CSV by index or name
- Prompts for velocity
- Builds concatenated EthernetKRL XML via MotionController.build_move_sequence_payload
- Prints payload and summary
"""
import sys
from pathlib import Path

# Make project modules importable
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from csvHelper import load_all_points_csv
from motion_controller import MotionController


class DummyTransport:
    def __init__(self):
        self.connected = True
        self.sent_payloads = []

    def send(self, data: bytes):
        self.sent_payloads.append(data)

    def receive(self, n: int) -> bytes:
        return b""


def choose_csv(default_name: str = "points.csv") -> str:
    csv_dir = PROJECT_ROOT
    try:
        csv_files = sorted([p.name for p in csv_dir.glob("*.csv")])
        if csv_files:
            print("Available CSV files:")
            for idx, name in enumerate(csv_files, start=1):
                print(f"  {idx}. {name}")
        else:
            print("No CSV files found; default will be used.")
    except Exception as e:
        print(f"WARNING: Could not list CSV files automatically: {e}")
        csv_files = []

    print(f"Default: {default_name}")
    choice = input("Enter index or filename (Enter = default): ").strip()

    if not choice:
        return default_name

    if choice.isdigit() and csv_files:
        idx = int(choice)
        if 1 <= idx <= len(csv_files):
            return csv_files[idx - 1]
        print("Invalid selection number. Using default.")
        return default_name

    # Treat as filename; add .csv if missing
    if not choice.endswith(".csv"):
        choice += ".csv"
    return choice


def prompt_velocity(default_vel: float = 0.2) -> float:
    raw = input("Enter velocity (0.1 - 10.0) [default=0.2]: ").strip()
    if not raw:
        return default_vel
    try:
        vel = float(raw)
        if 0.1 <= vel <= 10.0:
            return vel
    except ValueError:
        pass
    print(f"Invalid velocity. Using default {default_vel}")
    return default_vel


def main():
    print("=== Offline PTP Cartesian Sequence (Dry Run) ===")
    chosen_csv = choose_csv("points.csv")
    print(f"Loading points from '{chosen_csv}'...")

    try:
        points = load_all_points_csv(str(PROJECT_ROOT / chosen_csv))
    except Exception as e:
        print(f"ERROR loading CSV: {e}")
        return 1

    if not points:
        print("ERROR: No points found.")
        return 1

    print(f"Loaded {len(points)} points.")
    vel = prompt_velocity(0.2)

    # Build concatenated payload without sending
    mc = MotionController(transport=DummyTransport())
    payload = mc.build_move_sequence_payload(
        points=points,
        cmd_type=1,  # move
        mode=2,      # PTP Cartesian
        vel=vel,
        base=0,
        tool=0,
        blending=0.0,
    )

    text = payload.decode("utf-8", errors="ignore")
    print("\n=== Concatenated XML Payload ===")
    print(text)
    print("=== End Payload ===\n")
    print(f"Total moves: {len(points)} | Total bytes: {len(payload)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
