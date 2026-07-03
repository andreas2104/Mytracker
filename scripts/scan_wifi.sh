#!/usr/bin/env bash
set -euo pipefail

INTERFACE="${1:-wlan0}"

scan_nmcli() {
    nmcli -t -f SSID,SIGNAL,SECURITY dev wifi list 2>/dev/null | \
    while IFS=: read -r ssid signal enc; do
        [ -z "$ssid" ] && continue
        printf "%-30s  %5s  %s\n" "$ssid" "$signal" "$enc"
    done | sort -k2 -rn
}

scan_iwlist() {
    sudo iwlist "$INTERFACE" scan 2>/dev/null | awk '
    /ESSID:/ {
        sub(/.*ESSID:"/, ""); sub(/".*/, ""); ssid = $0
    }
    /Encryption/ {
        enc = index($0, "on") ? "WPA/WPA2" : "Open"
    }
    /Quality/ {
        qual = ""
        if (match($0, /Quality[=:][[:space:]]*([0-9]+)/, a)) qual = a[1]
        if (ssid != "" && qual != "") {
            printf "%-30s  %5s  %s\n", ssid, qual, enc
            ssid = ""; qual = ""; enc = ""
        }
    }'
}

main() {
    if command -v nmcli &>/dev/null; then
        scan_nmcli
        exit 0
    fi

    if ! command -v iwlist &>/dev/null; then
        echo "error: neither nmcli nor iwlist found" >&2
        echo "Install wireless-tools or NetworkManager" >&2
        exit 1
    fi

    if ! ip link show "$INTERFACE" &>/dev/null; then
        echo "error: interface $INTERFACE not found" >&2
        exit 1
    fi

    echo "[*] Scanning on $INTERFACE ..." >&2
    scan_iwlist
}

main
