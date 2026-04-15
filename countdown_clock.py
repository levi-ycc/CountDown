import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QHBoxLayout, QPushButton, QInputDialog
)
from PyQt6.QtCore import QTimer, Qt, QTime, QSize
from PyQt6.QtGui import QFont, QPainter, QColor, QPen


class CountdownClock(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Countdown")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )
        # WA_TranslucentBackground 讓 paintEvent 的圓角有效（跨平台）
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.interval_minutes = self._ask_duration()
        self.init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(100)
        self.update_timer()

        self._drag_pos = None

    # ── 透明背景 + 自繪圓角深色面板 ─────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(26, 26, 26, 230))   # #1a1a1a，略透明
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 14, 14)

    # ── 詢問使用者 ──────────────────────────────────────────────
    def _ask_duration(self):
        val, ok = QInputDialog.getInt(
            None, "Set Timer",
            "Minutes (1–99):",
            value=1, min=1, max=99
        )
        return val if ok else 1

    # ── 介面初始化 ───────────────────────────────────────────────
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 16, 20, 14)
        layout.setSpacing(8)

        # 主時間顯示 — 不設固定字體大小，留給下方自動計算
        self.time_label = QLabel("00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setFont(QFont("Courier New", 52, QFont.Weight.Bold))
        self.time_label.setStyleSheet("color: #f0f0f0; background: transparent;")
        # 確保文字不會被截斷（Windows 高 DPI 的關鍵）
        self.time_label.setMinimumHeight(self.time_label.sizeHint().height() + 12)
        layout.addWidget(self.time_label)

        # 按鈕列（預設隱藏）
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.setContentsMargins(0, 0, 0, 0)

        self.reset_btn = QPushButton("↺")
        self.reset_btn.setToolTip("Reset")
        self.reset_btn.clicked.connect(self.update_timer)

        self.change_btn = QPushButton("⚙")
        self.change_btn.setToolTip("Change duration")
        self.change_btn.clicked.connect(self.change_duration)

        self.close_btn = QPushButton("✕")
        self.close_btn.setToolTip("Close")
        self.close_btn.clicked.connect(self.close)

        self.btn_row = QWidget()
        self.btn_row.setStyleSheet("background: transparent;")
        self.btn_row.setLayout(btn_layout)
        self.btn_row.setVisible(False)

        for btn in (self.reset_btn, self.change_btn, self.close_btn):
            btn.setFixedSize(44, 44)
            btn_layout.addWidget(btn)

        layout.addWidget(self.btn_row)
        self.setLayout(layout)

        # 樣式：只設 QPushButton，背景交給 paintEvent
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(60, 60, 60, 200);
                color: #dddddd;
                border: 1px solid #555;
                border-radius: 8px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: rgba(90, 90, 90, 230);
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: rgba(120, 120, 120, 230);
            }
        """)

        # 只固定寬度，高度交給 adjustSize 根據內容自動計算
        self.setMinimumWidth(220)
        self.adjustSize()

    # ── 滑鼠進入 / 離開 ──────────────────────────────────────────
    def enterEvent(self, event):
        self.btn_row.setVisible(True)
        self.adjustSize()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.btn_row.setVisible(False)
        self.adjustSize()
        super().leaveEvent(event)

    # ── 更改時間 ─────────────────────────────────────────────────
    def change_duration(self):
        val, ok = QInputDialog.getInt(
            self, "Change Timer",
            "Minutes (1–99):",
            value=self.interval_minutes, min=1, max=99
        )
        if ok:
            self.interval_minutes = val
            self.update_timer()

    # ── 核心計時（與系統時鐘同步）───────────────────────────────
    def update_timer(self):
        current = QTime.currentTime()
        total_seconds = self.interval_minutes * 60
        elapsed = (current.minute() * 60 + current.second()) % total_seconds
        seconds_left = total_seconds - elapsed
        self._update_display(seconds_left)

    def _update_display(self, seconds_left):
        minutes = seconds_left // 60
        seconds = seconds_left % 60
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")

        if seconds_left <= 15:
            self.time_label.setStyleSheet("color: #39ff14; background: transparent;")
        else:
            self.time_label.setStyleSheet("color: #f0f0f0; background: transparent;")

    # ── 拖曳移動 ─────────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)


if __name__ == '__main__':
    # Windows 高 DPI 縮放支援
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    clock = CountdownClock()
    clock.show()
    sys.exit(app.exec())
