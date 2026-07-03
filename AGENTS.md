use for education test and for my local hotspot
# AGENTS - WiFi Test Hotspot & Wireless Password Auditor

This directory contains scripts and configurations for auditing wireless networks by testing all combinations of passwords and characters against target hotspots.

## Components

### Password Generator
- `scripts/gen_passwords.py` — Generates all possible password combinations from a given character set up to a configurable max length.
- Supports configurable character sets: alphanumeric, special chars, or custom.

### Wireless Scanner
- `scripts/scan_wifi.sh` — Scans for available wireless hotspots and lists SSIDs with signal strength and encryption type.

### Auth Tester
- `scripts/auth_test.py` — Attempts authentication against a target WPA/WPA2 hotspot using generated password combinations.
- Supports handshake capture and verification.

### Attack Launcher (Full Workflow)
- `scripts/attack.sh` — Interactive script that scans, lets you select an AP, then launches the brute-force attack.
- Automates: scan → select → configure → attack.

### Configuration
- `config/settings.yml` — Configure target SSID, character set, min/max password length, timeout, and interface.

## Dependencies

```bash
pip install -r requirements.txt              # Python deps (pywifi)
sudo apt install wireless-tools              # Linux: iwlist for scan_wifi.sh
```

## Usage — Full Workflow

### 1. Lister les points d'accès
```bash
sudo ./scripts/scan_wifi.sh [interface]
```

### 2. Lancer l'attaque complète (scan → sélection → bruteforce)
```bash
sudo ./scripts/attack.sh [interface]
```
- Scanne les réseaux disponibles
- Vous choisissez le SSID cible
- Configurez le charset, la longueur, la limite
- Lance la génération + test automatiquement

### 3. En une ligne (génération + test direct)
```bash
./scripts/auth_test.py --ssid "<SSID>" --charset all --min 8 --max 8 --limit 1000
```

## Exemple complet
```bash
# 1. Scanner
sudo ./scripts/scan_wifi.sh wlan0

# 2. Voir le SSID cible, puis lancer le dictionnaire
./scripts/gen_passwords.py --charset all --min 8 --max 8 | \
  sudo ./scripts/auth_test.py --ssid "MonWiFi" --interface wlan0
```

## Safety & Legal

Only use on networks you own or have explicit written permission to test. Unauthorised wireless testing is illegal in most jurisdictions.
