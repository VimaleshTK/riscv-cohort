#!/usr/bin/env python3
import argparse
import os
import re
import json

def search_in_file(filepath, pattern, regex=False, case_insensitive=False):
    """Search for mnemonics in a single file and return matches."""
    results = []
    flags = re.IGNORECASE if case_insensitive else 0

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f, start=1):
            # Skip comments
            if line.strip().startswith("#"):
                continue

            # Extract first token (the mnemonic is usually the first word)
            tokens = line.strip().split()
            if not tokens:
                continue
            mnemonic = tokens[0].lstrip("$pseudo_op").strip()

            if regex:
                if re.search(pattern, mnemonic, flags):
                    results.append({
                        "filename": os.path.basename(filepath),
                        "line_number": i,
                        "mnemonic": mnemonic
                    })
            else:
                if re.fullmatch(pattern, mnemonic, flags):
                    results.append({
                        "filename": os.path.basename(filepath),
                        "line_number": i,
                        "mnemonic": mnemonic
                    })
    return results


def main():
    parser = argparse.ArgumentParser(description="Search for RISC-V mnemonics in opcode files.")
    parser.add_argument("pattern", help="Mnemonic or regex pattern to search (e.g., ADD, LW)")
    parser.add_argument("-i", "--ignore-case", action="store_true", help="Case-insensitive search")
    parser.add_argument("-r", "--regex", action="store_true", help="Interpret pattern as regex")
    parser.add_argument("-o", "--output", default="search.json", help="Output JSON file")
    parser.add_argument("--repo-path", default=".", help="Path to riscv-opcodes repo")
    args = parser.parse_args()

    # Directories inside repo to scan
    search_dirs = ["opcodes", "extensions"]
    all_results = []

    print("Scanning opcode files...")
    for d in search_dirs:
        dir_path = os.path.join(args.repo_path, d)
        if not os.path.isdir(dir_path):
            continue

        for fname in os.listdir(dir_path):
            fpath = os.path.join(dir_path, fname)
            if os.path.isfile(fpath):
                matches = search_in_file(
                    fpath, args.pattern, regex=args.regex, case_insensitive=args.ignore_case
                )
                all_results.extend(matches)

    # Print results to terminal
    if all_results:
        print("Matched mnemonics:")
        for r in all_results:
            print(f"{r['mnemonic']}  (in {r['filename']} line {r['line_number']})")
    else:
        print("No matches found.")

    # Save JSON
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    print(f"Search complete. Results saved to {args.output}")


if __name__ == "__main__":
    main()
