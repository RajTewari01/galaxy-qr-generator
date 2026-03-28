from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel,
                             QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QMouseEvent


# ── Apple premium font stack ──────────────────────────────────
FONT = ('".AppleSystemUIFont", -apple-system, BlinkMacSystemFont, '
        '"SF Pro Display", "SF Pro Text", "Helvetica Neue", Arial, sans-serif')


class TrafficLightButton(QPushButton):
    """macOS-style traffic light window control."""

    def __init__(self, color, hover_color, icon_char="", parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border-radius: 6px;
                border: 0.5px solid rgba(0,0,0,0.25);
                font-size: 8px;
                font-weight: 800;
                font-family: {FONT};
                color: transparent;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                color: rgba(0,0,0,0.5);
            }}
        """)
        if icon_char:
            self.setText(icon_char)


class CustomTitleBar(QWidget):
    """Frameless title bar with macOS traffic lights."""

    def __init__(self, parent, theme_key):
        super().__init__(parent)
        self.parent_window = parent
        self.setFixedHeight(38)
        self.layout_box = QHBoxLayout(self)
        self.layout_box.setContentsMargins(16, 0, 16, 0)
        self.layout_box.setSpacing(0)

        # Traffic lights (macOS dimensions)
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

        self.title_label = QLabel("Galaxy QR Core", self)
        self.title_label.setStyleSheet(f"""
            color: rgba(255, 255, 255, 0.7);
            font-weight: 500;
            font-size: 13px;
            font-family: {FONT};
            letter-spacing: 0.5px;
        """)
        self.title_label.setAlignment(Qt.AlignCenter)

        self.layout_box.addStretch()
        self.layout_box.addWidget(self.title_label)
        self.layout_box.addStretch()
        self.layout_box.addSpacing(56)  # Keep label dead center

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


class GlassPanel(QFrame):
    """Premium frosted glass panel with mirror border."""

    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.setObjectName("GlassPanel")

        panel_col = theme.get("panel", "#141419")
        if panel_col.startswith("#") and len(panel_col) == 7:
            r = int(panel_col[1:3], 16)
            g = int(panel_col[3:5], 16)
            b = int(panel_col[5:7], 16)
            bg_col = f"rgba({r}, {g}, {b}, 0.45)"
        else:
            bg_col = "rgba(20, 20, 25, 0.45)"

        # Apple mirror glass aesthetic tinted by theme
        self.setStyleSheet(f"""
            QFrame#GlassPanel {{
                background-color: {bg_col};
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-top: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
            }}
        """)

        # Soft environmental shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)


class PrimaryButton(QPushButton):
    """Premium macOS generic generation button."""

    def __init__(self, text, theme, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(36)

        accent = theme.get("accent_grad", "#0A84FF")
        hover = theme.get("accent_hover", "#1A8CFF")

        shadow_hex = "#0A84FF"
        if accent.startswith("#"):
            shadow_hex = accent
        elif "stop:1 " in accent:
            shadow_hex = accent.split("stop:1 ")[1][:7]

        # Theme-aware Apple Glass Gradient style
        self.setStyleSheet(f"""
            QPushButton {{
                background: {accent};
                color: white;
                font-weight: 600;
                font-family: {FONT};
                font-size: 13px;
                letter-spacing: 0.5px;
                border: 1px solid rgba(0, 0, 0, 0.15);
                border-top: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background: {hover};
            }}
            QPushButton:pressed {{
                background: {accent};
            }}
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        try:
            r = int(shadow_hex[1:3], 16)
            g = int(shadow_hex[3:5], 16)
            b = int(shadow_hex[5:7], 16)
            shadow.setColor(QColor(r, g, b, 80))
        except Exception:
            shadow.setColor(QColor(10, 132, 255, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
