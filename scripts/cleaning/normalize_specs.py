import pandas as pd
from pathlib import Path
import re


BASE = Path("data/cleaned/merged")


# ============================================================
# 1. NORMALIZE MONITOR RESOLUTION
# ============================================================

monitor_file = BASE / "monitor_specs.csv"

df = pd.read_csv(monitor_file)


def normalize_resolution(value):

    if pd.isna(value):
        return value

    s = str(value).strip().lower()

    # Full HD / FHD
    if (
        "full hd" in s
        or s == "fhd"
        or "1920 x 1080" in s
        or "1920x1080" in s
    ):
        return "1920x1080"

    # QHD / 2K
    if (
        "qhd" in s
        or s == "2k"
        or "2560 x 1440" in s
        or "2560x1440" in s
    ):
        return "2560x1440"

    return value


df["resolution"] = df["resolution"].apply(
    normalize_resolution
)

df.to_csv(
    monitor_file,
    index=False,
    encoding="utf-8"
)

print("MONITOR resolution normalized")


# ============================================================
# 2. NORMALIZE KEYBOARD LAYOUT
# ============================================================

keyboard_file = BASE / "keyboard_specs.csv"

df = pd.read_csv(keyboard_file)


def normalize_layout(value):

    if pd.isna(value):
        return value

    s = str(value).strip()

    if s.lower() == "tkl":
        return "TKL"

    return s


df["layout"] = df["layout"].apply(
    normalize_layout
)

df.to_csv(
    keyboard_file,
    index=False,
    encoding="utf-8"
)

print("KEYBOARD layout normalized")


print()
print("=" * 70)
print("SPEC NORMALIZATION COMPLETED")
print("=" * 70)
