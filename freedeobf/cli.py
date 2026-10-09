from __future__ import annotations
import argparse
import pathlib
import sys
from .engine import deobfuscate

def main() -> int:
    parser = argparse.ArgumentParser(prog="freedeobf", description="Offline conservative source deobfuscation; input is never executed.")
    parser.add_argument("input", nargs="?", help="source file; stdin when omitted")
    parser.add_argument("-o", "--output", help="output file; stdout when omitted")
    parser.add_argument("--language", default="auto", choices=("auto", "lua", "luau", "javascript", "python"))
    parser.add_argument("--passes", type=int, default=3)
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()
    try:
        source = pathlib.Path(args.input).read_text(encoding="utf-8") if args.input else sys.stdin.read()
        output, report = deobfuscate(source, args.language, args.passes)
        if args.output:
            pathlib.Path(args.output).write_text(output, encoding="utf-8")
        else:
            sys.stdout.write(output)
        if args.report:
            for item in report:
                if item.changed: print(f"[+] {item.name}: {item.detail}", file=sys.stderr)
        return 0
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"freedeobf: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__": raise SystemExit(main())