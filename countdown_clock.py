import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QHBoxLayout, QPushButton, QInputDialog
)
from PyQt6.QtCore import QTimer, Qt, QTime, QEvent, QRect
from PyQt6.QtGui import QFont, QPainter, QColor, QCursor

RESIZE_MARGIN = 8  # px from edge to trigger resize


class CountdownClock(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Countdown")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)

        self.interval_minutes = self._ask_duration()

        self._drag_pos = None
        self._is_dragging = False
        self._resize_dir = None
        self._resize_start_pos = None
        self._resize_start_geom = None

        self.init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(100)
        self.update_timer()

    # ── 畫圓角深色背景（跨平台） ────────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(26, 26, 26, 220))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 14, 14)

    # ── 詢問使用者 ──────────────────────────────────────────────
    def _ask_duration(self):
        val, ok = QInputDialog.getInt(
            None, "Set Timer", "Minutes (1–99):",
            value=1, min=1, max=99
        )
        return val if ok else 1

    # ── 介面初始化 ───────────────────────────────────────────────
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 12)
        layout.setSpacing(8)

        self.time_label = QLabel("00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setFont(QFont("Courier New", 52, QFont.Weight.Bold))
        self.time_label.setStyleSheet("color: #f0f0f0; background: transparent;")
        layout.addWidget(self.time_label)

        # 按鈕列 ── 預設隱藏，但空間已預留（不影響視窗大小）
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.setContentsMargins(0, 0, 0, 0)

        self.reset_btn  = QPushButton("↺")
        self.change_btn = QPushButton("⚙")
        self.close_btn  = QPushButton("✕")

        self.reset_btn.setToolTip("Reset")
        self.change_btn.setToolTip("Change duration")
        self.close_btn.setToolTip("Close")

        self.reset_btn.clicked.connect(self.update_timer)
        self.change_btn.clicked.connect(self.change_duration)
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
                background-color: rgba(130, 130, 130, 230);
            }
        """)

        self.setMinimumSize(180, 120)
        self.resize(230, 165)   # 初始大小：預留按鈕區，show/hide 不改視窗大小

        # ── 讓所有非按鈕子控件把滑鼠事件轉給主視窗 ──────────────
        for child in self.findChildren(QWidget):
            if not isinstance(child, QPushButton):
                child.setMouseTracking(True)
                child.installEventFilter(self)

    # ── 滑鼠進入 / 離開 ──────────────────────────────────────────
    def enterEvent(self, event):
        self.btn_row.setVisible(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.btn_row.setVisible(False)
        super().leaveEvent(event)

    # ── 更改時間 ─────────────────────────────────────────────────
    def change_duration(self):
        val, ok = QInputDialog.getInt(
            self, "Change Timer", "Minutes (1–99):",
            value=self.interval_minutes, min=1, max=99
        )
        if ok:
            self.interval_minutes = val
            self.update_timer()

    # ── 計時（與系統時鐘同步） ───────────────────────────────────
    def update_timer(self):
        current = QTime.currentTime()
        total = self.interval_minutes * 60
        elapsed = (current.minute() * 60 + current.second()) % total
        self._update_display(total - elapsed)

    def _update_display(self, seconds_left):
        m, s = divmod(seconds_left, 60)
        self.time_label.setText(f"{m:02d}:{s:02d}")
        if seconds_left <= 15:
            self.time_label.setStyleSheet("color: #39ff14; background: transparent;")  # 螢光綠
        elif seconds_left <= 60:
            self.time_label.setStyleSheet("color: #ff4444; background: transparent;")  # 紅色
        else:
            self.time_label.setStyleSheet("color: #f0f0f0; background: transparent;")  # 亮白

    # ── 邊緣偵測（決定縮放方向） ─────────────────────────────────
    def _get_resize_dir(self, pos):
        x, y, w, h, m = pos.x(), pos.y(), self.width(), self.height(), RESIZE_MARGIN
        left   = x < m
        right  = x > w - m
        top    = y < m
        bottom = y > h - m
        if left  and top:    return 'tl'
        if right and top:    return 'tr'
        if left  and bottom: return 'bl'
        if right and bottom: return 'br'
        if left:  return 'l'
        if right: return 'r'
        if top:   return 't'
        if bottom: return 'b'
        return None

    def _cursor_for_dir(self, d):
        if d in ('tl', 'br'): return Qt.CursorShape.SizeFDiagCursor
        if d in ('tr', 'bl'): return Qt.CursorShape.SizeBDiagCursor
        if d in ('l',  'r'):  return Qt.CursorShape.SizeHorCursor
        if d in ('t',  'b'):  return Qt.CursorShape.SizeVerCursor
        return Qt.CursorShape.ArrowCursor

    # ── 主視窗滑鼠事件（邊緣縮放 + 拖曳） ───────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            d = self._get_resize_dir(pos)
            if d:
                self._resize_dir       = d
                self._resize_start_pos  = event.globalPosition().toPoint()
                self._resize_start_geom = self.geometry()
                self._is_dragging = False
            else:
                self._drag_pos    = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                self._is_dragging = True
                self._resize_dir  = None

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()

        # 沒有按下按鍵時：只更新游標外觀
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            d = self._get_resize_dir(pos)
            self.setCursor(self._cursor_for_dir(d) if d else Qt.CursorShape.OpenHandCursor)
            return

        # 縮放
        if self._resize_dir and self._resize_start_pos:
            gp  = event.globalPosition().toPoint()
            dx  = gp.x() - self._resize_start_pos.x()
            dy  = gp.y() - self._resize_start_pos.y()
            geo = QRect(self._resize_start_geom)
            d   = self._resize_dir
            if 'r' in d: geo.setRight(geo.right()   + dx)
            if 'b' in d: geo.setBottom(geo.bottom() + dy)
            if 'l' in d: geo.setLeft(geo.left()     + dx)
            if 't' in d: geo.setTop(geo.top()       + dy)
            if geo.width() >= self.minimumWidth() and geo.height() >= self.minimumHeight():
                self.setGeometry(geo)

        # 拖曳
        elif self._is_dragging and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._resize_dir  = None
        self._drag_pos    = None
        self._is_dragging = False
        self.setCursor(Qt.CursorShape.ArrowCursor)

    # ── 子控件滑鼠事件轉發（讓整個視窗可拖曳） ──────────────────
    def eventFilter(self, obj, event):
        t = event.type()
        if t == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                self._drag_pos    = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                self._is_dragging = True
                self._resize_dir  = None
        elif t == QEvent.Type.MouseMove:
            if (event.buttons() & Qt.MouseButton.LeftButton) and self._is_dragging and self._drag_pos:
                self.move(event.globalPosition().toPoint() - self._drag_pos)
        elif t == QEvent.Type.MouseButtonRelease:
            self._drag_pos    = None
            self._is_dragging = False
        return super().eventFilter(obj, event)


if __name__ == '__main__':
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    clock = CountdownClock()
    clock.show()
    sys.exit(app.exec())
