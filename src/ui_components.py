from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel,
                             QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QMouseEvent


# ── Apple system font stack ──────────────────────────────────
FONT = '".AppleSystemUIFont", -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, Helvetica, Arial, sans-serif'


class TrafficLightButton(QPushButton):
    """macOS-style traffic light window control."""

    def __init__(self, color, hover_color, icon_char="", parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self.setCursor(Qt.PointingHandCursor)
        self._icon = icon_char
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border-radius: 6px;
                border: 0.5px solid rgba(0,0,0,0.2);
                font-size: 8px;
                font-weight: bold;
                color: transparent;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                color: rgba(0,0,0,0.6);
            }}
        """)
        if icon_char:
            self.setText(icon_char)


class CustomTitleBar(QWidget):
    """Frameless title bar with macOS traffic lights and centered title."""

    def __init__(self, parent, theme_key, theme):
        super().__init__(parent)
        self.parent_window = parent
        self.theme = theme
        self.setFixedHeight(38)
        self.layout_box = QHBoxLayout(self)
        self.layout_box.setContentsMargins(16, 0, 16, 0)
        self.layout_box.setSpacing(0)

        # Traffic lights — Big Sur style sizing
        self.btn_close = TrafficLightButton("#FF5F56", "#FF5F56", "✕", self)
        self.btn_min = TrafficLightButton("#FFBD2E", "#FFBD2E", "−", self)
        self.btn_max = TrafficLightButton("#27C93F", "#27C93F", "+", self)

        self.btn_close.clicked.connect(self.parent_window.close)
        self.btn_min.clicked.connect(self.parent_window.showMinimized)
        self.btn_max.clicked.connect(self.toggle_max)

        self.layout_box.addWidget(self.btn_close)
        self.layout_box.addSpacing(8)
        self.layout_box.addWidget(self.btn_min)
        self.layout_box.addSpacing(8)
        self.layout_box.addWidget(self.btn_max)

        self.title_label = QLabel(f"Galaxy QR", self)
        self.title_label.setStyleSheet(f"""
            color: rgba(255, 255, 255, 0.85);
            font-weight: 500;
            font-size: 13px;
            font-family: {FONT};
        """)
        self.title_label.setAlignment(Qt.AlignCenter)

        self.layout_box.addStretch()
        self.layout_box.addWidget(self.title_label)
        self.layout_box.addStretch()
        self.layout_box.addSpacing(56) # Offset to keep title centered

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


class MacContainer(QFrame):
    """Standard macOS grouped container style."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MacContainer")
        self.setStyleSheet(f"""
            QFrame#MacContainer {{
                background-color: #1E1E1E; /* System gray 6 dark */
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)


class PrimaryButton(QPushButton):
    """macOS primary action button (solid blue accent)."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(28)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #0A84FF; /* macOS Dark Mode Blue */
                color: white;
                font-weight: 500;
                font-family: {FONT};
                font-size: 13px;
                border: none;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #329AFF;
            }}
            QPushButton:pressed {{
                background-color: #006ADA;
            }}
            QPushButton:disabled {{
                background-color: rgba(255, 255, 255, 0.1);
                color: rgba(255, 255, 255, 0.25);
            }}
        """)
