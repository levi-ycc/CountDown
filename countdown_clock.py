import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import QTimer, Qt, QTime
from PyQt6.QtGui import QFont

class CountdownClock(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("1 Min Realtime Timer")
        
        # 強迫置頂 (Always on Top)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        self.init_ui()
        
        # 使用 100 毫秒的高頻更新，確保能精準抓到系統真實時間的跳動
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(100)
        self.update_timer()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        self.time_label = QLabel("00:60", self)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setFont(QFont("Arial", 48, QFont.Weight.Bold))
        self.time_label.setStyleSheet("color: #e74c3c;")
        self.layout.addWidget(self.time_label)
        
        self.setLayout(self.layout)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f7f7f7;
                border-radius: 10px;
            }
        """)
        self.setFixedSize(200, 120)

    def update_timer(self):
        # 取得系統當前時間
        current_time = QTime.currentTime()
        
        # 距離下一分鐘剩餘的秒數 (60 - 當前秒數)
        seconds_passed = current_time.second()
        seconds_left = 60 - seconds_passed
        
        # 如果剛好是 0 秒，我們顯示 60 還是 0？這邊維持顯示 00:60 或 00:00，通常倒數顯示 60
        # 為了格式統一，我們把它顯示為 00:xx
        if seconds_left == 60:
            display_text = "00:60"
        else:
            display_text = f"00:{seconds_left:02d}"
            
        self.time_label.setText(display_text)
        
        # 小於等於 15 秒時為綠色，大於則為紅色
        if seconds_left <= 15:
            self.time_label.setStyleSheet("color: #27ae60;") # 綠色
        else:
            self.time_label.setStyleSheet("color: #e74c3c;") # 紅色

if __name__ == '__main__':
    app = QApplication(sys.argv)
    clock = CountdownClock()
    clock.show()
    sys.exit(app.exec())
