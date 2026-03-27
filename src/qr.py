import sys
import urllib.parse
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QComboBox, QFrame, QGraphicsDropShadowEffect, 
                             QColorDialog)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import (QColor, QRadialGradient, QBrush, QPainter, QFont, QPixmap, QImage, QMouseEvent)

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import (
    RadialGradiantColorMask, VerticalGradiantColorMask,
    HorizontalGradiantColorMask, SquareGradiantColorMask
)
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

try:
    from BlurWindow.blurWindow import GlobalBlur
except ImportError:
    GlobalBlur = None

# ======================= DATA MAPPING =========================
INPUT_MAP = {
    "Website/URL": ["Paste URL"],
    "Wi-Fi Config": ["SSID (Network Name)", "Password", "Type (WPA/WEP)"],
    "Plain Text": ["Enter Text"],
    "vCard (Contact)": ["Full Name", "Phone", "Email", "Organization"],
    "Send SMS": ["Phone Number", "Message"],
    "Send Email": ["To Email", "Subject", "Body"],
    "WhatsApp Msg": ["Phone (w/ Country Code)", "Message"],
    "YouTube Video": ["Video ID"],
    "UPI (India)": ["UPI ID", "Payee Name", "Amount (Optional)"],
    "Geo Coords": ["Latitude", "Longitude"],
}

# ======================= LOGIC ENGINE =========================
class QrLogic:
    def format_data(self, mode, i):
        try:
            if not i or not i[0]: return "Empty"
            if mode == "Website/URL" or mode == "Plain Text": return i[0]
            if mode == "Wi-Fi Config": return f"WIFI:S:{i[0]};T:{i[2]};P:{i[1]};;"
            if mode == "Send SMS": return f"SMSTO:{i[0]}:{i[1]}"
            if mode == "Send Email": return f"mailto:{i[0]}?subject={i[1]}&body={i[2]}"
            if mode == "WhatsApp Msg": return f"https://wa.me/{i[0]}?text={urllib.parse.quote(i[1])}"
            if mode == "UPI (India)": return f"upi://pay?pa={i[0]}&pn={urllib.parse.quote(i[1])}"
            return i[0]
        except:
            return "Error"

    def generate_image(self, data, gradient_type, colors):
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
        qr.add_data(data)
        qr.make(fit=True)

        mask_map = {
            "Radial": RadialGradiantColorMask, "Vertical": VerticalGradiantColorMask,
            "Horizontal": HorizontalGradiantColorMask, "Square": SquareGradiantColorMask
        }
        
        rgb_colors = []
        for c in colors:
            if isinstance(c, str):
                c = c.lstrip('#')
                rgb_colors.append(tuple(int(c[i:i+2], 16) for i in (0, 2, 4)))
            else:
                rgb_colors.append((c.red(), c.green(), c.blue()))

        bg = rgb_colors[0]
        c_start = rgb_colors[1]
        c_end = rgb_colors[2]

        mask_cls = mask_map.get(gradient_type, RadialGradiantColorMask)
        if gradient_type == "Vertical":
            mask = mask_cls(back_color=bg, top_color=c_start, bottom_color=c_end)
        elif gradient_type == "Horizontal":
            mask = mask_cls(back_color=bg, left_color=c_start, right_color=c_end)
        else:
            mask = mask_cls(back_color=bg, center_color=c_start, edge_color=c_end)

        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            color_mask=mask
        )
        return img

# ======================= UI COMPONENTS =========================

class TrafficLightButton(QPushButton):
    def __init__(self, color, hover_color, parent=None):
        super().__init__(parent)
        self.setFixedSize(14, 14)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border-radius: 7px;
                border: 1px solid rgba(0,0,0,0.1);
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)

class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(40)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 0, 15, 0)
        
        self.btn_close = TrafficLightButton("#FF605C", "#FF4A45")
        self.btn_min = TrafficLightButton("#FFBD44", "#FFB024")
        self.btn_max = TrafficLightButton("#00CA4E", "#00B843")
        
        self.btn_close.clicked.connect(self.parent.close)
        self.btn_min.clicked.connect(self.parent.showMinimized)
        self.btn_max.clicked.connect(self.toggle_max)
        
        self.layout.addWidget(self.btn_close)
        self.layout.addSpacing(2)
        self.layout.addWidget(self.btn_min)
        self.layout.addSpacing(2)
        self.layout.addWidget(self.btn_max)
        
        self.title_label = QLabel("Galaxy Core Engine")
        self.title_label.setStyleSheet("color: rgba(255,255,255,0.75); font-weight: 500; font-size: 13px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;")
        self.title_label.setAlignment(Qt.AlignCenter)
        
        self.layout.addStretch()
        self.layout.addWidget(self.title_label)
        self.layout.addStretch()
        self.layout.addSpacing(50) 
        
        self._is_tracking = False
        self._start_pos = None

    def toggle_max(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()
            
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._is_tracking = True
            self._start_pos = event.globalPos() - self.parent.frameGeometry().topLeft()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_tracking:
            self.parent.move(event.globalPos() - self._start_pos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._is_tracking = False

class GlassFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(25, 25, 35, 120); 
                border: 1px solid rgba(255, 255, 255, 15);
                border-radius: 16px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 10)
        self.setGraphicsEffect(shadow)

class NeonButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(45)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00f260, stop:1 #0575e6);
                color: white;
                font-weight: 600;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI";
                font-size: 14px;
                border: none;
                border-radius: 22px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00e055, stop:1 #0465c5);
            }
            QPushButton:pressed {
                padding-top: 2px;
            }
        """)

class GalaxyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logic = QrLogic()
        self.colors = [QColor("white"), QColor("#00f260"), QColor("#0575e6")] 
        
        # Frameless Window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.resize(1000, 700)
        self.center_window()
        
        # Apply Windows Blur if available
        if sys.platform == 'win32' and GlobalBlur:
            try:
                GlobalBlur(self.winId(), Dark=True, HWND=self.winId())
            except Exception:
                pass

        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("""
            QWidget#CentralWidget {
                background-color: rgba(18, 18, 25, 220);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 20);
            }
        """)
        self.central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Custom Title Bar
        self.title_bar = CustomTitleBar(self)
        self.main_layout.addWidget(self.title_bar)
        
        # Content Layout
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(40, 20, 40, 40)
        
        self.glass_panel = GlassFrame()
        self.glass_panel_layout = QHBoxLayout(self.glass_panel)
        self.glass_panel_layout.setContentsMargins(30, 30, 30, 30)
        self.glass_panel_layout.setSpacing(30)
        
        self.content_layout.addWidget(self.glass_panel)
        self.main_layout.addLayout(self.content_layout)
        
        # LEFT PANEL
        self.left_panel = QVBoxLayout()
        title = QLabel("SYSTEM CONFIG")
        title.setStyleSheet("color: #00f260; font-weight: 600; font-family: -apple-system; font-size: 13px; letter-spacing: 1px;")
        self.left_panel.addWidget(title)
        
        lbl_mode = QLabel("Data Protocol")
        lbl_mode.setStyleSheet("color: rgba(255,255,255,0.6); margin-top: 10px; font-family: -apple-system;")
        self.left_panel.addWidget(lbl_mode)
        
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(INPUT_MAP.keys())
        self.combo_mode.setStyleSheet(self.get_input_style())
        self.combo_mode.currentIndexChanged.connect(self.update_inputs)
        self.left_panel.addWidget(self.combo_mode)
        
        lbl_grad = QLabel("Gradient Field")
        lbl_grad.setStyleSheet("color: rgba(255,255,255,0.6); margin-top: 10px; font-family: -apple-system;")
        self.left_panel.addWidget(lbl_grad)
        
        self.combo_grad = QComboBox()
        self.combo_grad.addItems(["Radial", "Vertical", "Horizontal", "Square"])
        self.combo_grad.setStyleSheet(self.get_input_style())
        self.left_panel.addWidget(self.combo_grad)

        lbl_col = QLabel("Visual Spectrum")
        lbl_col.setStyleSheet("color: rgba(255,255,255,0.6); margin-top: 10px; font-family: -apple-system;")
        self.left_panel.addWidget(lbl_col)
        
        btn_layout = QHBoxLayout()
        self.btn_bg = self.create_color_btn("BG", 0)
        self.btn_c = self.create_color_btn("Core", 1)
        self.btn_e = self.create_color_btn("Edge", 2)
        btn_layout.addWidget(self.btn_bg)
        btn_layout.addWidget(self.btn_c)
        btn_layout.addWidget(self.btn_e)
        self.left_panel.addLayout(btn_layout)

        self.left_panel.addStretch()
        self.glass_panel_layout.addLayout(self.left_panel, 35)
        
        # RIGHT PANEL
        self.right_panel = QVBoxLayout()
        self.input_widget = QWidget()
        self.input_layout = QVBoxLayout(self.input_widget)
        self.input_layout.setContentsMargins(0,0,0,0)
        self.right_panel.addWidget(self.input_widget)
        
        self.preview_lbl = QLabel()
        self.preview_lbl.setAlignment(Qt.AlignCenter)
        self.preview_lbl.setStyleSheet("""
            QLabel {
                background-color: rgba(0,0,0,0.2);
                border: 1px solid rgba(255,255,255,0.05);
                border-radius: 12px;
            }
        """)
        self.preview_lbl.setMinimumSize(280, 280)
        self.right_panel.addWidget(self.preview_lbl)
        
        self.right_panel.addSpacing(20)
        
        self.btn_gen = NeonButton("INITIALIZE GENERATION")
        self.btn_gen.clicked.connect(self.generate)
        self.right_panel.addWidget(self.btn_gen)
        
        self.glass_panel_layout.addLayout(self.right_panel, 65)

        self.update_inputs()

    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

    def get_input_style(self):
        return """
            QWidget {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI";
                font-size: 13px;
            }
            QWidget:focus {
                border: 1px solid rgba(0, 242, 96, 0.8);
                background-color: rgba(255, 255, 255, 0.08);
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #202028;
                border-radius: 8px;
                color: white;
                selection-background-color: #0575e6;
            }
        """

    def create_color_btn(self, text, idx):
        btn = QPushButton(text)
        btn.setFixedHeight(35)
        btn.setStyleSheet(f"background-color: {self.colors[idx].name()}; color: black; font-weight: 500; font-family: -apple-system; border-radius: 8px; border: none;")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda: self.pick_color(idx, btn))
        return btn

    def pick_color(self, idx, btn):
        col = QColorDialog.getColor()
        if col.isValid():
            self.colors[idx] = col
            txt_col = "black" if (col.red()*0.299 + col.green()*0.587 + col.blue()*0.114) > 186 else "white"
            btn.setStyleSheet(f"background-color: {col.name()}; color: {txt_col}; font-weight: 500; font-family: -apple-system; border-radius: 8px; border: none;")

    def update_inputs(self):
        for i in reversed(range(self.input_layout.count())): 
            self.input_layout.itemAt(i).widget().setParent(None)
        
        mode = self.combo_mode.currentText()
        fields = INPUT_MAP.get(mode, ["Input"])
        
        self.current_entries = []
        for f in fields:
            l = QLabel(f.upper())
            l.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 10px; font-weight: 600; font-family: -apple-system; margin-top: 5px; letter-spacing: 0.5px;")
            self.input_layout.addWidget(l)
            
            e = QLineEdit()
            e.setPlaceholderText(f"Enter {f}...")
            e.setStyleSheet(self.get_input_style())
            self.input_layout.addWidget(e)
            self.current_entries.append(e)
        
        self.right_panel.addStretch()

    def generate(self):
        inputs = [e.text() for e in self.current_entries]
        mode = self.combo_mode.currentText()
        grad = self.combo_grad.currentText()
        
        data_str = self.logic.format_data(mode, inputs)
        pil_img = self.logic.generate_image(data_str, grad, self.colors)
        
        im_data = pil_img.convert("RGBA").tobytes("raw", "RGBA")
        qim = QImage(im_data, pil_img.size[0], pil_img.size[1], QImage.Format_RGBA8888)
        pix = QPixmap.fromImage(qim)
        
        self.preview_lbl.setPixmap(pix.scaled(280, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GalaxyWindow()
    window.show()
    sys.exit(app.exec_())