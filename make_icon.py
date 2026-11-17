"""Draws icon.png (dark tile + pink-to-cyan glasses). Run once: QT_QPA_PLATFORM=offscreen python3 make_icon.py"""
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QGuiApplication, QImage, QLinearGradient, QPainter, QPen

app = QGuiApplication([])
img = QImage(256, 256, QImage.Format.Format_ARGB32)
img.fill(Qt.GlobalColor.transparent)
p = QPainter(img)
p.setRenderHint(QPainter.RenderHint.Antialiasing)
p.setBrush(QColor("#1d1530")); p.setPen(Qt.PenStyle.NoPen)
p.drawRoundedRect(QRectF(8, 8, 240, 240), 52, 52)
g = QLinearGradient(30, 0, 226, 0); g.setColorAt(0, QColor("#ff5ec4")); g.setColorAt(1, QColor("#3fe0ff"))
pen = QPen(QBrush(g), 16); pen.setCapStyle(Qt.PenCapStyle.RoundCap); p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)
p.drawRoundedRect(QRectF(30, 88, 82, 76), 24, 24)
p.drawRoundedRect(QRectF(144, 88, 82, 76), 24, 24)
p.drawArc(QRectF(108, 90, 40, 40), 20 * 16, 140 * 16)
p.end()
img.save("icon.png")
