#!/usr/bin/env python3
import itertools
import argparse
import sys
import signal

signal.signal(signal.SIGPIPE, signal.SIG_DFL)

PRESETS = {
    "alpha": "abcdefghijklmnopqrstuvwxyz",
    "ALPHA": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "digit": "0123456789",
    "alphanumeric": "abcdefghijklmnopqrstuvwxyz0123456789",
    "ALPHANUMERIC": "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    "special": "!@#$%^&*()_+|}>?",
    "all": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+|}>?",
}


def resolve_charset(raw):
    if raw in PRESETS:
        return PRESETS[raw]
    return raw


def generate(charset, min_len, max_len):
    for length in range(min_len, max_len + 1):
        for combo in itertools.product(charset, repeat=length):
            yield ''.join(combo)


def main():
    presets_help = ", ".join(sorted(PRESETS))
    parser = argparse.ArgumentParser(
        description="Generate all possible password combinations from a charset.")
    parser.add_argument("--charset", default="alphanumeric",
                        help=f"Character set or preset name ({presets_help}) "
                             "(default: alphanumeric)")
    parser.add_argument("--min", type=int, default=8,
                        help="Minimum password length (default: 8)")
    parser.add_argument("--max", type=int, default=8,
                        help="Maximum password length (default: 8)")
    parser.add_argument("--limit", type=int, default=0,
                        help="Stop after this many passwords (0 = unlimited)")
    args = parser.parse_args()

    charset = resolve_charset(args.charset)

    if args.min < 1:
        print("error: --min must be >= 1", file=sys.stderr)
        sys.exit(1)
    if args.max < args.min:
        print("error: --max must be >= --min", file=sys.stderr)
        sys.exit(1)

    count = 0
    for pw in generate(charset, args.min, args.max):
        print(pw)
        count += 1
        if args.limit and count >= args.limit:
            break


if __name__ == "__main__":
    main()
