import os
import json
from collections import defaultdict

EXT_DIR = "extensions"       # folder with pseudo-op files
OUTPUT_JSON = "combinations.json"

def parse_val(v):
    if v is None:
        return None
    v = str(v)
    try:
        if v.startswith("0x") or v.startswith("0X"):
            return int(v, 16)
        else:
            return int(v)
    except:
        return v

def parse_pseudo_ops():
    results = defaultdict(set)

    for fname in os.listdir(EXT_DIR):
        fpath = os.path.join(EXT_DIR, fname)
        if not os.path.isfile(fpath):
            continue

        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line.startswith("$pseudo_op"):
                    continue

                parts = line.split()
                try:
                    ext = parts[1].split("::")[0].upper()
                except IndexError:
                    continue

                opcode = funct3 = funct7 = None
                for p in parts[5:]:
                    if p.startswith("6..2="):
                        opcode = parse_val(p.split("=")[1])
                    elif p.startswith("14..12="):
                        funct3 = parse_val(p.split("=")[1])
                    elif p.startswith("31..25="):
                        funct7 = parse_val(p.split("=")[1])

                if opcode is not None:
                    results[ext].add((opcode, funct3, funct7))

    # Convert sets to list of dicts, sorted
    json_results_sorted = {}
    for ext in sorted(results.keys()):
        tuples_sorted = sorted(results[ext], key=lambda x: (
            x[0] if x[0] is not None else -1,
            x[1] if x[1] is not None else -1,
            x[2] if x[2] is not None else -1
        ))
        json_results_sorted[ext] = [
            {"opcode": t[0], "funct3": t[1], "funct7": t[2]} for t in tuples_sorted
        ]

    return json_results_sorted

def main():
    combinations = parse_pseudo_ops()
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(combinations, f, indent=4)
    print(f"Saved {len(combinations)} extensions to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
