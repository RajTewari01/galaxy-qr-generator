import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPixmap, QImage
from themes import THEMES
from engine import QrLogic, INPUT_MAP
from ui_components import CustomTitleBar, GlassFrame, NeonButton

class GalaxyWindow(QMainWindow):
    def __init__(self, theme_key):
        super().__init__()
        self.theme = THEMES.get(theme_key, THEMES["apple-dark"])
        self.theme_key = theme_key
        self.logic = QrLogic()
        self.colors = [QColor("white"), QColor("#00f260"), QColor("#0575e6")] 
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(1000, 700)

        self.central_widget = QWidget(self)
        self.central_widget.setStyleSheet(f"""
            QWidget#CentralWidget {{
                background-color: {self.theme['bg']};
                border-radius: 12px;
                border: 1px solid {self.theme['border']};
            }}
        """)
        self.central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_bar = CustomTitleBar(self, self.theme_key, self.theme)
        self.main_layout.addWidget(self.title_bar)
        
        self.main_h_layout = QHBoxLayout()
        self.main_h_layout.addStretch()
        
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(20, 10, 20, 30)
        
        self.glass_panel = GlassFrame(self.theme, self)
        self.glass_panel.setMaximumWidth(960) 
        self.glass_panel_layout = QHBoxLayout(self.glass_panel)
        self.glass_panel_layout.setContentsMargins(30, 30, 30, 30)
        self.glass_panel_layout.setSpacing(40)
        
        self.content_layout.addWidget(self.glass_panel)
        
        self.main_h_layout.addLayout(self.content_layout)
        self.main_h_layout.addStretch()
        self.main_layout.addLayout(self.main_h_layout)
        
        # LEFT PANEL
        self.left_panel = QVBoxLayout()
        title = QLabel(f"SYSTEM CONFIG | {self.theme_key.upper()}")
        title.setStyleSheet(f"color: {self.theme['text']}; font-weight: 600; font-family: -apple-system; font-size: 13px; letter-spacing: 1px;")
        self.left_panel.addWidget(title)
        
        lbl_mode = QLabel("Data Protocol")
        lbl_mode.setStyleSheet(f"color: {self.theme['text_dim']}; margin-top: 10px; font-family: -apple-system;")
        self.left_panel.addWidget(lbl_mode)
        
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(INPUT_MAP.keys())
        self.combo_mode.setStyleSheet(self.get_input_style())
        self.combo_mode.currentIndexChanged.connect(self.update_inputs)
        self.left_panel.addWidget(self.combo_mode)
        
        lbl_grad = QLabel("Gradient Field")
        lbl_grad.setStyleSheet(f"color: {self.theme['text_dim']}; margin-top: 10px; font-family: -apple-system;")
        self.left_panel.addWidget(lbl_grad)
        
        self.combo_grad = QComboBox()
        self.combo_grad.addItems(["Radial", "Vertical", "Horizontal", "Square"])
        self.combo_grad.setStyleSheet(self.get_input_style())
        self.left_panel.addWidget(self.combo_grad)

        lbl_col = QLabel("Visual Spectrum")
        lbl_col.setStyleSheet(f"color: {self.theme['text_dim']}; margin-top: 10px; font-family: -apple-system;")
        self.left_panel.addWidget(lbl_col)
        
        btn_layout = QHBoxLayout()
        
        # We need a color dialog implementation or skip it.
        # Implemented simplified color picking in logic or inline.
        from PyQt5.QtWidgets import QColorDialog
        
        def pick_col(idx, b):
            c = QColorDialog.getColor(self.colors[idx], self)
            if c.isValid():
                self.colors[idx] = c
                txt = "black" if (c.red()*0.299 + c.green()*0.587 + c.blue()*0.114) > 186 else "white"
                b.setStyleSheet(f"background-color: {c.name()}; color: {txt}; font-weight: 600; font-family: -apple-system; border-radius: 8px; border: none;")

        self.btn_bg = QPushButton("BG")
        self.btn_c = QPushButton("Core")
        self.btn_e = QPushButton("Edge")
        
        for idx, btn in enumerate([self.btn_bg, self.btn_c, self.btn_e]):
            btn.setFixedHeight(35)
            btn.setStyleSheet(f"background-color: {self.colors[idx].name()}; color: black; font-weight: 600; font-family: -apple-system; border-radius: 8px; border: none;")
            btn.setCursor(Qt.PointingHandCursor)
            
        self.btn_bg.clicked.connect(lambda _, b=self.btn_bg: pick_col(0, b))
        self.btn_c.clicked.connect(lambda _, b=self.btn_c: pick_col(1, b))
        self.btn_e.clicked.connect(lambda _, b=self.btn_e: pick_col(2, b))
        
        btn_layout.addWidget(self.btn_bg)
        btn_layout.addWidget(self.btn_c)
        btn_layout.addWidget(self.btn_e)
        
        self.left_panel.addLayout(btn_layout)
        self.left_panel.addStretch()
        self.glass_panel_layout.addLayout(self.left_panel, 40)
        
        # RIGHT PANEL
        self.right_panel = QVBoxLayout()
        self.input_widget = QWidget()
        self.input_layout = QVBoxLayout(self.input_widget)
        self.input_layout.setContentsMargins(0,0,0,0)
        self.right_panel.addWidget(self.input_widget)
        
        self.preview_lbl = QLabel()
        self.preview_lbl.setAlignment(Qt.AlignCenter)
        self.preview_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {self.theme['bg']};
                border: 1px solid {self.theme['border']};
                border-radius: 12px;
            }}
        """)
        self.preview_lbl.setMinimumSize(320, 320)
        self.right_panel.addWidget(self.preview_lbl)
        
        self.right_panel.addSpacing(20)
        
        self.btn_gen = NeonButton("INITIALIZE GENERATION", self.theme)
        self.btn_gen.clicked.connect(self.generate)
        self.right_panel.addWidget(self.btn_gen)
        
        self.glass_panel_layout.addLayout(self.right_panel, 60)

        self.update_inputs()

    def get_input_style(self):
        return f"""
            QWidget {{
                background-color: {self.theme['input_bg']};
                border: 1px solid {self.theme['border']};
                color: {self.theme['text']};
                padding: 10px;
                border-radius: 8px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI";
                font-size: 13px;
            }}
            QWidget:focus {{
                border: 1px solid {self.theme.get('accent_hover', '#fff')};
            }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{
                background-color: {self.theme['bg']};
                border: 1px solid {self.theme['border']};
                border-radius: 8px;
                color: {self.theme['text']};
                selection-background-color: rgba(255,255,255,0.1);
            }}
        """

    def update_inputs(self):
        for i in reversed(range(self.input_layout.count())): 
            w = self.input_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        
        mode = self.combo_mode.currentText()
        fields = INPUT_MAP.get(mode, ["Input"])
        
        self.current_entries = []
        for f in fields:
            l = QLabel(f.upper())
            l.setStyleSheet(f"color: {self.theme['text_dim']}; font-size: 10px; font-weight: 600; font-family: -apple-system; margin-top: 5px; letter-spacing: 0.5px;")
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
        
        self.preview_lbl.setPixmap(pix.scaled(320, 320, Qt.KeepAspectRatio, Qt.SmoothTransformation))
