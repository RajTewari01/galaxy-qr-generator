from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QMouseEvent

class TrafficLightButton(QPushButton):
    def __init__(self, color, hover_color, parent=None):
        super().__init__(parent)
        self.setFixedSize(14, 14)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border-radius: 7px;
                border: 1px solid rgba(0,0,0,0.3);
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)

class CustomTitleBar(QWidget):
    def __init__(self, parent, theme_key, theme):
        super().__init__(parent)
        self.parent_window = parent
        self.theme = theme
        self.setFixedHeight(40)
        self.layout_box = QHBoxLayout(self)
        self.layout_box.setContentsMargins(15, 0, 15, 0)
        
        self.btn_close = TrafficLightButton("#FF605C", "#FF4A45", self)
        self.btn_min = TrafficLightButton("#FFBD44", "#FFB024", self)
        self.btn_max = TrafficLightButton("#00CA4E", "#00B843", self)
        
        self.btn_close.clicked.connect(self.parent_window.close)
        self.btn_min.clicked.connect(self.parent_window.showMinimized)
        self.btn_max.clicked.connect(self.toggle_max)
        
        self.layout_box.addWidget(self.btn_close)
        self.layout_box.addSpacing(2)
        self.layout_box.addWidget(self.btn_min)
        self.layout_box.addSpacing(2)
        self.layout_box.addWidget(self.btn_max)
        
        self.title_label = QLabel(f"Galaxy Core Engine | {theme_key.upper()}", self)
        self.title_label.setStyleSheet(f"color: {theme['text_dim']}; font-weight: 600; font-size: 13px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;")
        self.title_label.setAlignment(Qt.AlignCenter)
        
        self.layout_box.addStretch()
        self.layout_box.addWidget(self.title_label)
        self.layout_box.addStretch()
        self.layout_box.addSpacing(60)
        
        self._is_tracking = False
        self._start_pos = None

    def toggle_max(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
        else:
            self.parent_window.showMaximized()
            
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._is_tracking = True
            self._start_pos = event.globalPos() - self.parent_window.frameGeometry().topLeft()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_tracking and self._start_pos is not None:
            self.parent_window.move(event.globalPos() - self._start_pos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._is_tracking = False

class GlassFrame(QFrame):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {theme['panel']}; 
                border: 1px solid {theme['border']};
                border-radius: 16px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)

class NeonButton(QPushButton):
    def __init__(self, text, theme, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(45)
        self.setStyleSheet(f"""
            QPushButton {{
                background: {theme['accent_grad']};
                color: {theme['text']};
                font-weight: 600;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI";
                font-size: 14px;
                border: none;
                border-radius: 22px;
            }}
            QPushButton:hover {{
                background: {theme['accent_hover']};
            }}
            QPushButton:pressed {{
                padding-top: 2px;
            }}
        """)
