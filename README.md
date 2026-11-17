# NerdrKeys for Linux

A tiny system tray cheat sheet for your [herdr](https://herdr.dev) keyboard shortcuts, built for
KDE Plasma (Wayland). A Linux port of [svhong/nerdrkeys](https://github.com/svhong/nerdrkeys) for macOS.

Click the glasses icon in the tray to see:

- **Your shortcuts**: every `[[keys.command]]` in your herdr config
- **herdr's built-in keys**: panes, tabs, workspaces and general, including any you've remapped under `[keys]`

It re-reads `~/.config/herdr/config.toml` (or `$HERDR_CONFIG_PATH`) every time it opens.

- Filter box to narrow the list
- **A− / A+** for text size (80%–160%, remembered)
- **TOML** button opens your herdr config
- **Pin** keeps the window open when it loses focus (Esc closes it)
- Single instance: launching it again just opens the popup
- If you've pinned it to the task bar (via `install.sh`), the pinned icon lights up while the popup is open

## Requirements

Python 3.11+ and PySide6 (`sudo dnf install python3-pyside6`).

## Run

```bash
python3 nerdrkeys.py          # tray app
python3 nerdrkeys.py --dump   # print what it parsed from your config
./install.sh                  # add an app-menu entry you can pin to the task bar
```

## Notes

- On Wayland, apps can't position their own windows, so KDE decides where the popup appears.
- Plugin actions show their `description`, or the raw command ID. Add friendly names to `FRIENDLY`
  in `nerdrkeys.py`.
- New herdr built-in actions need adding to `BUILTINS`.
- `make_icon.py` regenerates `icon.png`.
