#!/usr/bin/env bash
# Installs the NerdrKeys launcher (app menu entry + icon) for the current user.
# Re-run it if you move this folder.
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
apps="$HOME/.local/share/applications"
mkdir -p "$apps"
cat > "$apps/nerdrkeys.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=NerdrKeys
Comment=herdr shortcut cheat sheet in the system tray
Exec=python3 $dir/nerdrkeys.py
Icon=$dir/icon.png
Categories=Utility;
Terminal=false
StartupNotify=false
DESKTOP
update-desktop-database "$apps" 2>/dev/null || true
command -v kbuildsycoca6 >/dev/null && kbuildsycoca6 >/dev/null 2>&1 || true
echo "Installed. Search 'NerdrKeys' in the app launcher, then right-click > Pin to Task Manager."
echo "To start at login: cp $apps/nerdrkeys.desktop ~/.config/autostart/"
