import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QHBoxLayout, QPushButton, QInputDialog
)
from PyQt6.QtCore import QTimer, Qt, QTime
from PyQt6.QtGui import QFont


class CountdownClock(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Countdown")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 預設 1 分鐘；啟動時詢問使用者
        self.interval_minutes = self._ask_duration()

        self.init_ui()

        # 100 ms 高頻更新，與系統時鐘同步
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(100)
        self.update_timer()

        # 拖曳用變數
        self._drag_pos = None

    # ── 詢問使用者 ──────────────────────────────────────────────
    def _ask_duration(self):
        val, ok = QInputDialog.getInt(
            None, "設定倒數時間",
            "請輸入倒數分鐘數（1–99）：",
            value=1, min=1, max=99
        )
        return val if ok else 1

    # ── 介面初始化 ───────────────────────────────────────────────
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 14, 20, 12)
        layout.setSpacing(6)

        # 主時間顯示
        self.time_label = QLabel("00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setFont(QFont("Courier New", 56, QFont.Weight.Bold))
        self.time_label.setStyleSheet("color: #f0f0f0; background: transparent;")
        layout.addWidget(self.time_label)

        # 按鈕列（預設隱藏）
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.reset_btn = QPushButton("↺")
        self.reset_btn.setToolTip("重設")
        self.reset_btn.clicked.connect(self.update_timer)

        self.change_btn = QPushButton("⚙")
        self.change_btn.setToolTip("更改時間")
        self.change_btn.clicked.connect(self.change_duration)

        self.close_btn = QPushButton("✕")
        self.close_btn.setToolTip("關閉")
        self.close_btn.clicked.connect(self.close)

        self.btn_row = QWidget()
        self.btn_row.setLayout(btn_layout)
        self.btn_row.setVisible(False)  # 預設隱藏

        for btn in (self.reset_btn, self.change_btn, self.close_btn):
            btn.setFixedSize(40, 40)
            btn_layout.addWidget(btn)

        layout.addWidget(self.btn_row)
        self.setLayout(layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 14px;
            }
            QPushButton {
                background-color: #2e2e2e;
                color: #dddddd;
                border: 1px solid #444;
                border-radius: 8px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #444444;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #606060;
            }
        """)

        self.setFixedWidth(220)
        self._update_window_height(buttons_visible=False)

    def _update_window_height(self, buttons_visible: bool):
        self.setFixedHeight(110 if not buttons_visible else 148)

    # ── 滑鼠進入 / 離開：顯示 / 隱藏按鈕 ───────────────────────
    def enterEvent(self, event):
        self.btn_row.setVisible(True)
        self._update_window_height(buttons_visible=True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.btn_row.setVisible(False)
        self._update_window_height(buttons_visible=False)
        super().leaveEvent(event)

    # ── 更改倒數時間 ─────────────────────────────────────────────
    def change_duration(self):
        val, ok = QInputDialog.getInt(
            self, "更改倒數時間",
            "請輸入倒數分鐘數（1–99）：",
            value=self.interval_minutes, min=1, max=99
        )
        if ok:
            self.interval_minutes = val
            self.update_timer()

    # ── 核心計時邏輯（與系統時鐘同步）──────────────────────────
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
            self.time_label.setStyleSheet("color: #39ff14; background: transparent;")  # 螢光綠
        else:
            self.time_label.setStyleSheet("color: #f0f0f0; background: transparent;")  # 亮白

    # ── 拖曳移動視窗 ─────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    clock = CountdownClock()
    clock.show()
    sys.exit(app.exec())
