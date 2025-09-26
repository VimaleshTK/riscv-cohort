import os
import re

def collect_opcodes(base_dir):
    mnemonics = set()
    for root, _, files in os.walk(base_dir):
        for fname in files:
            path = os.path.join(root, fname)
            try:
                with open(path) as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        mnemonic = line.split()[0].strip()
                        # only keep mnemonics starting with a-z
                        if not re.match(r'^[a-z]', mnemonic):
                            continue
                        mnemonics.add(mnemonic)
            except Exception:
                continue
    return mnemonics

def main():
    base_dirs = [d for d in ('opcodes', 'extensions') if os.path.isdir(d)]
    all_mn = set()
    for d in base_dirs:
        all_mn.update(collect_opcodes(d))
    sorted_mn = sorted(all_mn)
    with open('all_opcodes.txt', 'w') as out:
        out.write('\n'.join(sorted_mn))
    print(f"{len(sorted_mn)} opcodes written to all_opcodes.txt")

if __name__ == '__main__':
    main()
