import os
from collections import defaultdict

EXT_DIR = "extensions"       # folder containing pseudo-op files
OUTPUT_TXT = "opcode_frequencies.txt"

def parse_pseudo_ops():
    opcode_map = defaultdict(list)

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
                    mnemonic = parts[2]
                except IndexError:
                    continue

                opcode = None
                for p in parts[5:]:
                    if p.startswith("6..2="):
                        val = p.split("=")[1]
                        if val.startswith("0x") or val.startswith("0X"):
                            opcode = int(val, 16)
                        else:
                            opcode = int(val)
                        break

                if opcode is not None:
                    opcode_map[opcode].append(mnemonic)

    return opcode_map

def main():
    opcode_map = parse_pseudo_ops()

    with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
        for opcode in sorted(opcode_map.keys()):
            mnemonics = sorted(set(opcode_map[opcode]))
            count = len(mnemonics)
            line = f"{opcode} ({count} instructions): {', '.join(mnemonics)}\n"
            f.write(line)
            print(line.strip())

    print(f"\nSaved opcode frequencies to {OUTPUT_TXT}")

if __name__ == "__main__":
    main()
