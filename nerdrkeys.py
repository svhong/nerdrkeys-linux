#!/usr/bin/env python3
"""NerdrKeys for Linux (KDE Plasma): a tray cheat sheet for herdr keyboard shortcuts.

Re-reads ~/.config/herdr/config.toml (or $HERDR_CONFIG_PATH) every time it opens.
Run with --dump to print what was parsed.
"""
import os
import sys
import tomllib

BUILTINS = [  # (config name, default binding, label, group)
    ("split_vertical", "prefix+v", "Split right", "Panes"),
    ("split_horizontal", "prefix+minus", "Split down", "Panes"),
    ("focus_pane_left", "prefix+h", "Focus left", "Panes"),
    ("focus_pane_down", "prefix+j", "Focus down", "Panes"),
    ("focus_pane_up", "prefix+k", "Focus up", "Panes"),
    ("focus_pane_right", "prefix+l", "Focus right", "Panes"),
    ("cycle_pane_next", "prefix+tab", "Next pane", "Panes"),
    ("zoom", "prefix+z", "Zoom pane", "Panes"),
    ("close_pane", "prefix+x", "Close pane", "Panes"),
    ("resize_mode", "prefix+r", "Resize mode", "Panes"),
    ("rename_pane", "prefix+shift+p", "Rename pane", "Panes"),
    ("edit_scrollback", "prefix+e", "Edit scrollback", "Panes"),
    ("new_tab", "prefix+c", "New tab", "Tabs"),
    ("next_tab", "prefix+n", "Next tab", "Tabs"),
    ("previous_tab", "prefix+p", "Previous tab", "Tabs"),
    ("switch_tab", "prefix+1..9", "Go to tab 1–9", "Tabs"),
    ("rename_tab", "prefix+shift+t", "Rename tab", "Tabs"),
    ("close_tab", "prefix+shift+x", "Close tab", "Tabs"),
    ("new_workspace", "prefix+shift+n", "New workspace", "Workspaces"),
    ("workspace_picker", "prefix+w", "Workspace picker", "Workspaces"),
    ("goto", "prefix+g", "Go to…", "Workspaces"),
    ("rename_workspace", "prefix+shift+w", "Rename workspace", "Workspaces"),
    ("close_workspace", "prefix+shift+d", "Close workspace", "Workspaces"),
    ("new_worktree", "prefix+shift+g", "New git worktree", "Workspaces"),
    ("next_agent", "", "Next agent", "Workspaces"),
    ("previous_agent", "", "Previous agent", "Workspaces"),
    ("toggle_sidebar", "prefix+b", "Toggle sidebar", "General"),
    ("help", "prefix+?", "Help", "General"),
    ("settings", "prefix+s", "Settings", "General"),
    ("reload_config", "prefix+shift+r", "Reload config", "General"),
    ("open_notification_target", "prefix+o", "Open notification", "General"),
    ("detach", "prefix+q", "Detach", "General"),
]

FRIENDLY = {
    "ray.plugin-manager.open": "Plugin Manager",
    "persiyanov.reviewr.toggle": "reviewr (diff review)",
    "iuhoay.break-pane.break": "Break pane → new tab",
    "iuhoay.break-pane.break-to-workspace": "Break pane → new workspace",
    "iuhoay.break-pane.move-to-workspace": "Move pane → workspace",
    "hhdebb.herdr-radar.view-flip": "Radar: active ↔ recent",
    "hhdebb.herdr-radar.settings": "Radar settings",
}

SYMBOLS = {
    "ctrl": "Ctrl+", "shift": "⇧", "alt": "Alt+", "option": "Alt+", "cmd": "Super+",
    "super": "Super+", "minus": "-", "comma": ",", "tab": "⇥", "enter": "↩",
    "esc": "esc", "left": "←", "right": "→", "up": "↑", "down": "↓", "space": "space",
}


def config_path():
    return os.environ.get("HERDR_CONFIG_PATH") or os.path.expanduser("~/.config/herdr/config.toml")


def load_shortcuts():
    """Returns (prefix, [(group title, [(keys, label)])], error)."""
    path, error, cfg = config_path(), None, {}
    try:
        with open(path, "rb") as f:
            cfg = tomllib.load(f)
    except FileNotFoundError:
        error = f"No config at {path} (showing defaults)"
    except (OSError, tomllib.TOMLDecodeError) as e:
        error = f"Couldn't read {path}: {e}"

    keys = cfg.get("keys", {})
    prefix = keys.get("prefix", "ctrl+b")
    overrides = {k: v for k, v in keys.items() if isinstance(v, str)}

    mine = []
    for c in keys.get("command", []):
        k = c.get("key")
        if not k:
            continue
        cmd = c.get("command", "")
        desc = c.get("description", "")
        label = FRIENDLY.get(cmd) or (desc[:1].upper() + desc[1:] if desc else cmd)
        mine.append((k, label))

    groups = [("Your shortcuts", mine)] if mine else []
    by_group = {}
    for name, default, label, group in BUILTINS:
        binding = overrides.get(name, default)
        if binding:
            by_group.setdefault(group, []).append((binding, label))
    groups += list(by_group.items())
    return prefix, groups, error


def pretty_keys(binding, prefix):
    """'prefix+shift+c' -> ['Ctrl+B', '⇧C']: prefix chord, then the key."""
    def chord(s):
        out = []
        for part in s.split("+"):
            p = part.lower()
            out.append(SYMBOLS.get(p) or (p.upper() if len(p) == 1 else p))
        return "".join(out)

    parts = binding.split("+")
    if parts[0].lower() == "prefix":
        return [chord(prefix), chord("+".join(parts[1:]))]
    return [chord(binding)]


def main():
    if "--dump" in sys.argv:
        prefix, groups, error = load_shortcuts()
        print(f"prefix: {prefix}" + (f"  [{error}]" if error else ""))
        for title, items in groups:
            print(f"\n{title}")
            for keys, label in items:
                print(f"  {label:32} {' then '.join(pretty_keys(keys, prefix))}")
        return

    from PySide6.QtNetwork import QLocalServer, QLocalSocket
    from PySide6.QtCore import QEvent, QPointF, QRectF, QSettings, Qt, QUrl
    from PySide6.QtGui import QAction, QColor, QCursor, QDesktopServices, QIcon, QPainter, QPen, QPixmap, QLinearGradient, QBrush
    from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel, QLineEdit, QMenu,
                                   QPushButton, QScrollArea, QSystemTrayIcon, QVBoxLayout, QWidget)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("nerdrkeys")
    settings = QSettings("nerdrkeys", "nerdrkeys")
    app.setDesktopFileName("nerdrkeys")   # matches nerdrkeys.desktop so the task manager shows our icon

    # Single instance: if one is already running, ask it to open its popup and exit.
    sock_name = f"nerdrkeys-{os.getuid()}"
    probe = QLocalSocket()
    probe.connectToServer(sock_name)
    if probe.waitForConnected(300):
        probe.write(b"show"); probe.waitForBytesWritten(300)
        return
    QLocalServer.removeServer(sock_name)   # clear a stale socket from a crash
    server = QLocalServer()
    server.listen(sock_name)

    def glasses_icon():
        """Two lenses and a bridge, in a pink-to-cyan gradient."""
        pm = QPixmap(64, 64)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QLinearGradient(0, 0, 64, 0)   # pink -> cyan: readable on light and dark panels
        grad.setColorAt(0, QColor("#ff5ec4"))
        grad.setColorAt(1, QColor("#3fe0ff"))
        pen = QPen(QBrush(grad), 6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawRoundedRect(QRectF(4, 20, 25, 22), 7, 7)
        p.drawRoundedRect(QRectF(35, 20, 25, 22), 7, 7)
        p.drawArc(QRectF(26, 20, 12, 12), 20 * 16, 140 * 16)
        p.end()
        return QIcon(pm)

    class Popup(QWidget):
        def __init__(self):
            # Not Qt.Popup: Wayland refuses popup grabs from a tray click. Use a plain
            # frameless window and close it when it loses focus instead.
            super().__init__(None, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
            self.setAutoFillBackground(True)
            self.armed = False
            self.scale = min(max(float(settings.value("textScale", 1.0)), 0.8), 1.6)
            outer = QVBoxLayout(self)
            outer.setContentsMargins(0, 0, 0, 0)
            outer.setSpacing(0)

            self.header = QLabel()
            self.filter = QLineEdit(placeholderText="Filter…")
            self.filter.textChanged.connect(self.render)
            self.list = QLabel()
            self.list.setTextFormat(Qt.TextFormat.RichText)
            self.list.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.list.setWordWrap(True)
            scroll = QScrollArea(widgetResizable=True, frameShape=QFrame.Shape.NoFrame)
            scroll.setWidget(self.list)

            top = QVBoxLayout()
            top.setContentsMargins(12, 12, 12, 8)
            top.addWidget(self.header)
            top.addWidget(self.filter)
            outer.addLayout(top)
            outer.addWidget(scroll, 1)

            bar = QHBoxLayout()
            bar.setContentsMargins(12, 6, 12, 8)
            edit = QPushButton("TOML", flat=True)
            edit.setToolTip("Open herdr config.toml")
            edit.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(config_path())))
            smaller, self.pct, bigger = QPushButton("A−", flat=True), QPushButton(flat=True), QPushButton("A+", flat=True)
            smaller.clicked.connect(lambda: self.bump(-0.1))
            bigger.clicked.connect(lambda: self.bump(0.1))
            self.pct.clicked.connect(lambda: self.bump(None))
            quit_ = QPushButton("Quit", flat=True)
            quit_.clicked.connect(app.quit)
            self.pin = QPushButton(flat=True, checkable=True)
            icon = QIcon.fromTheme("pin")   # Breeze's pin icon; emoji if the theme lacks it
            if icon.isNull():
                self.pin.setText("📌")
            else:
                self.pin.setIcon(icon)
            self.pin.setToolTip("Keep open when you click elsewhere")
            bar.addWidget(edit)
            bar.addWidget(self.pin)
            bar.addStretch()
            for w in (smaller, self.pct, bigger):
                bar.addWidget(w)
            bar.addStretch()
            bar.addWidget(quit_)
            outer.addLayout(bar)

        def bump(self, delta):
            self.scale = 1.0 if delta is None else min(max(round((self.scale + delta) * 10) / 10, 0.8), 1.6)
            settings.setValue("textScale", self.scale)
            self.resize_to_scale()
            self.render()

        def resize_to_scale(self):
            self.setFixedSize(round(340 * self.scale), 480)

        def render(self):
            s, q = self.scale, self.filter.text().lower()
            pal = app.palette()
            dim = pal.color(pal.ColorRole.PlaceholderText).name()
            cap_bg = pal.color(pal.ColorRole.Mid).name()
            cap = lambda t: (f'<span style="background-color:{cap_bg}; font-size:{11*s:.0f}px">'
                             f'&nbsp;{t.replace("<", "&lt;")}&nbsp;</span>')
            html = []
            if self.error:
                html.append(f'<p style="color:#e5484d">{self.error}</p>')
            for title, items in self.groups:
                rows = [(k, l) for k, l in items if q in l.lower()]
                if not rows:
                    continue
                html.append(f'<p style="color:{dim}; font-size:{10*s:.0f}px; margin:10px 0 2px">{title.upper()}</p>')
                html.append('<table width="100%" cellspacing="3">')
                for keys, label in rows:
                    caps = f' <span style="color:{dim}; font-size:{9*s:.0f}px">then</span> '.join(
                        cap(c) for c in pretty_keys(keys, self.prefix))
                    html.append(f'<tr><td style="font-size:{12*s:.0f}px">{label}</td>'
                                f'<td align="right">{caps}</td></tr>')
                html.append("</table>")
            self.list.setText("".join(html))
            self.list.setContentsMargins(12, 0, 12, 8)
            self.pct.setText(f"{round(self.scale * 100)}%")
            self.header.setText(f'<span style="font-size:{14*s:.0f}px">herdr shortcuts</span> '
                                f'&nbsp;&nbsp;<span style="color:{dim}; font-size:{11*s:.0f}px">'
                                f'prefix {pretty_keys(self.prefix, self.prefix)[0]}</span>')

        def open_at_cursor(self):
            self.prefix, self.groups, self.error = load_shortcuts()
            self.filter.clear()
            self.resize_to_scale()
            self.render()
            screen = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
            area = screen.availableGeometry()
            pos = QCursor.pos()
            x = min(max(pos.x() - self.width() // 2, area.left() + 8), area.right() - self.width() - 8)
            y = pos.y() + 12 if pos.y() < area.center().y() else pos.y() - self.height() - 12
            y = min(max(y, area.top() + 8), area.bottom() - self.height() - 8)
            self.move(x, y)
            self.armed = False
            self.show()
            self.raise_()
            self.activateWindow()
            self.filter.setFocus()

        def event(self, e):
            if e.type() == QEvent.Type.WindowActivate:
                self.armed = True
            elif e.type() == QEvent.Type.WindowDeactivate and self.armed and not self.pin.isChecked():
                self.armed = False
                self.hide()
            return super().event(e)

        def keyPressEvent(self, e):
            if e.key() == Qt.Key.Key_Escape:
                self.pin.setChecked(False)
                self.hide()

    popup = Popup()
    def on_new_connection():
        conn = server.nextPendingConnection()
        conn.readyRead.connect(lambda: (conn.readAll(), popup.open_at_cursor()))
    server.newConnection.connect(on_new_connection)

    app.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")))
    tray = QSystemTrayIcon(glasses_icon())
    tray.setToolTip("herdr shortcuts")

    def on_activated(reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.MiddleClick):
            popup.hide() if popup.isVisible() else popup.open_at_cursor()

    tray.activated.connect(on_activated)
    menu = QMenu()
    menu.addAction("Quit").triggered.connect(app.quit)
    tray.setContextMenu(menu)
    tray.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
