import os
import csv
from collections import Counter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OPCODES_DIR = os.path.join(BASE_DIR, "opcodes")
EXT_DIR = os.path.join(BASE_DIR, "extensions")
OUTPUT_CSV = os.path.join(BASE_DIR, "extension_counts.csv")

def parse_opcodes_dir(counts):
    """Parse opcodes/ files (rv32i, rv64m, etc.) if present."""
    if not os.path.isdir(OPCODES_DIR):
        return
    for fname in os.listdir(OPCODES_DIR):
        fpath = os.path.join(OPCODES_DIR, fname)
        if not os.path.isfile(fpath):
            continue
        ext = fname.upper()
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                counts[ext] += 1

def parse_extensions_dir(counts):
    """Parse extensions/ files ($pseudo_op lines)."""
    if not os.path.isdir(EXT_DIR):
        return
    for fname in os.listdir(EXT_DIR):
        fpath = os.path.join(EXT_DIR, fname)
        if not os.path.isfile(fpath):
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line.startswith("$pseudo_op"):
                    continue
                try:
                    ext = line.split()[1].split("::")[0]
                    counts[ext.upper()] += 1
                except Exception:
                    continue

def print_table(counts):
    print(f"{'Extension':<15} | Count")
    print("-" * 25)
    for ext, cnt in sorted(counts.items()):
        print(f"{ext:<15} | {cnt}")

def save_csv(counts, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Extension", "Count"])
        for ext, cnt in sorted(counts.items()):
            writer.writerow([ext, cnt])


def main():
    counts = Counter()
    parse_opcodes_dir(counts)
    parse_extensions_dir(counts)
    if counts:
        print_table(counts)
        save_csv(counts, OUTPUT_CSV)
        print(f"\nResults saved to {OUTPUT_CSV}")
    else:
        print("No instructions found. Check that 'opcodes/' or 'extensions/' exists.")

if __name__ == "__main__":
    main()
