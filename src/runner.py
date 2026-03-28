import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QLineEdit, QPushButton,
                             QColorDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPixmap, QImage
from themes import THEMES
from engine import QrLogic, INPUT_MAP
from ui_components import CustomTitleBar, MacContainer, PrimaryButton, FONT


class GalaxyWindow(QMainWindow):
    def __init__(self, theme_key):
        super().__init__()
        self.theme = THEMES.get(theme_key, THEMES["apple-dark"])
        self.theme_key = theme_key
        self.logic = QrLogic()
        self.colors = [QColor("#ffffff"), QColor("#00f260"), QColor("#0575e6")]

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(800, 560) # more standard mac window aspect ratio

        # ── Central widget ───────────────────────────────
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("CentralWidget")
        self.central_widget.setStyleSheet(f"""
            QWidget#CentralWidget {{
                background-color: #282828; /* Standard macOS Dark Window Background */
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
        """)
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # ── Title bar ────────────────────────────────────
        self.title_bar = CustomTitleBar(self, self.theme_key, self.theme)
        self.main_layout.addWidget(self.title_bar)

        # ── Content area ─────────────────────────────────
        content_wrapper = QHBoxLayout()
        content_wrapper.setContentsMargins(20, 20, 20, 20)

        # Wrap everything in macOS style grouped container
        self.mac_panel = MacContainer(self)
        self.mac_layout = QHBoxLayout(self.mac_panel)
        self.mac_layout.setContentsMargins(24, 24, 24, 24)
        self.mac_layout.setSpacing(32)

        content_wrapper.addWidget(self.mac_panel)
        self.main_layout.addLayout(content_wrapper)

        # ── Left panel ───────────────────────────────────
        self._build_left_panel()

        # ── Right panel ──────────────────────────────────
        self._build_right_panel()

        self.update_inputs()

    # ─────────────────────────────────────────────────────
    #  Left panel: config controls
    # ─────────────────────────────────────────────────────
    def _build_left_panel(self):
        left = QVBoxLayout()
        left.setSpacing(12)
        left.setContentsMargins(0, 0, 0, 0)
        left.setAlignment(Qt.AlignTop)

        # Protocol selector
        left.addWidget(self._section_label("Protocol"))
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(INPUT_MAP.keys())
        self.combo_mode.setStyleSheet(self._combo_style())
        self.combo_mode.setFixedHeight(26)
        self.combo_mode.currentIndexChanged.connect(self.update_inputs)
        left.addWidget(self.combo_mode)

        # Gradient selector
        left.addWidget(self._section_label("Gradient"))
        self.combo_grad = QComboBox()
        self.combo_grad.addItems(["Radial", "Vertical", "Horizontal", "Square"])
        self.combo_grad.setStyleSheet(self._combo_style())
        self.combo_grad.setFixedHeight(26)
        left.addWidget(self.combo_grad)

        # Colors
        left.addWidget(self._section_label("Colors"))
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.btn_bg = self._make_color_btn(0, "Background")
        self.btn_c = self._make_color_btn(1, "Center")
        self.btn_e = self._make_color_btn(2, "Edge")

        btn_row.addWidget(self.btn_bg)
        btn_row.addWidget(self.btn_c)
        btn_row.addWidget(self.btn_e)
        left.addLayout(btn_row)

        self.mac_layout.addLayout(left, 45)

    # ─────────────────────────────────────────────────────
    #  Right panel: inputs, preview, generate
    # ─────────────────────────────────────────────────────
    def _build_right_panel(self):
        right = QVBoxLayout()
        right.setSpacing(16)
        right.setContentsMargins(0, 0, 0, 0)
        right.setAlignment(Qt.AlignTop)

        self.input_widget = QWidget()
        self.input_layout = QVBoxLayout(self.input_widget)
        self.input_layout.setContentsMargins(0, 0, 0, 0)
        self.input_layout.setSpacing(10)
        right.addWidget(self.input_widget)

        # QR preview
        self.preview_lbl = QLabel()
        self.preview_lbl.setAlignment(Qt.AlignCenter)
        self.preview_lbl.setFixedSize(240, 240)
        self.preview_lbl.setStyleSheet("""
            QLabel {
                background-color: #2D2D2D;
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 8px;
            }
        """)

        preview_row = QHBoxLayout()
        preview_row.addStretch()
        preview_row.addWidget(self.preview_lbl)
        preview_row.addStretch()
        right.addLayout(preview_row)

        # Generate button
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_gen = PrimaryButton("Generate QR Code", self)
        self.btn_gen.setMinimumWidth(120)
        self.btn_gen.clicked.connect(self.generate)
        btn_row.addWidget(self.btn_gen)
        right.addLayout(btn_row)

        self.mac_layout.addLayout(right, 55)

    # ─────────────────────────────────────────────────────
    #  Style helpers
    # ─────────────────────────────────────────────────────
    def _section_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"""
            color: rgba(255, 255, 255, 0.55);
            font-size: 11px;
            font-weight: 500;
            font-family: {FONT};
            padding-top: 8px;
        """)
        return lbl

    def _combo_style(self):
        # Precise macOS native look for combobox
        return f"""
            QComboBox {{
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(0, 0, 0, 0.5);
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                color: white;
                padding: 0px 8px;
                border-radius: 5px;
                font-family: {FONT};
                font-size: 13px;
            }}
            QComboBox:hover {{
                background-color: rgba(255, 255, 255, 0.15);
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
                subcontrol-position: right center;
            }}
            QComboBox::down-arrow {{
                image: none;
                width: 0;
            }}
            QComboBox QAbstractItemView {{
                background-color: #2D2D2D;
                border: 1px solid rgba(0, 0, 0, 0.7);
                border-radius: 5px;
                color: white;
                selection-background-color: #0A84FF;
                padding: 2px;
                outline: 0;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 4px 8px;
                border-radius: 3px;
                min-height: 20px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: #0A84FF;
                color: white;
            }}
        """

    def _input_style(self):
        # macOS input fields
        return f"""
            QLineEdit {{
                background-color: rgba(255, 255, 255, 0.05); /* inset look */
                border: 1px solid rgba(0, 0, 0, 0.5);
                border-top: 1px solid rgba(0, 0, 0, 0.8);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                color: white;
                padding: 2px 6px;
                border-radius: 5px;
                font-family: {FONT};
                font-size: 13px;
                selection-background-color: #0A84FF;
            }}
            QLineEdit:hover {{
                background-color: rgba(255, 255, 255, 0.08);
            }}
            QLineEdit:focus {{
                border: 2px solid #0A84FF;
                background-color: rgba(255, 255, 255, 0.08);
                padding: 1px 5px;
            }}
            QLineEdit::placeholder {{
                color: rgba(255, 255, 255, 0.3);
            }}
        """

    # ─────────────────────────────────────────────────────
    #  Color picker buttons
    # ─────────────────────────────────────────────────────
    def _make_color_btn(self, idx, label):
        btn = QPushButton()
        btn.setFixedHeight(24)
        btn.setCursor(Qt.PointingHandCursor)
        self._apply_color_btn_style(btn, self.colors[idx])
        btn.clicked.connect(lambda _, b=btn, i=idx: self._pick_color(i, b))
        return btn

    def _apply_color_btn_style(self, btn, color):
        if isinstance(color, QColor):
            r, g, b = color.red(), color.green(), color.blue()
        else:
            hex_col = str(color)
            r = int(hex_col[1:3], 16)
            g = int(hex_col[3:5], 16)
            b = int(hex_col[5:7], 16)

        # macOS standard buttons have light border, semi-transparent top, dark transparent shadow
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba({r}, {g}, {b}, 1.0);
                border: 1px solid rgba(0, 0, 0, 0.3);
                border-top: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border: 1px solid rgba(255, 255, 255, 0.6);
            }}
            QPushButton:pressed {{
                background-color: rgba({r}, {g}, {b}, 0.8);
            }}
        """)

    def _pick_color(self, idx, btn):
        c = QColorDialog.getColor(self.colors[idx], self)
        if c.isValid():
            self.colors[idx] = c
            self._apply_color_btn_style(btn, c)

    # ─────────────────────────────────────────────────────
    #  Dynamic input fields
    # ─────────────────────────────────────────────────────
    def update_inputs(self):
        for i in reversed(range(self.input_layout.count())):
            w = self.input_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        mode = self.combo_mode.currentText()
        fields = INPUT_MAP.get(mode, ["Input"])

        self.current_entries = []
        for f in fields:
            row = QVBoxLayout()
            row.setSpacing(4)
            
            lbl = QLabel(f)
            lbl.setStyleSheet(f"""
                color: rgba(255, 255, 255, 0.85);
                font-size: 13px;
                font-weight: 400;
                font-family: {FONT};
            """)
            row.addWidget(lbl)

            entry = QLineEdit()
            entry.setPlaceholderText("...")
            entry.setFixedHeight(26)
            entry.setStyleSheet(self._input_style())
            row.addWidget(entry)
            
            self.input_layout.addLayout(row)
            self.current_entries.append(entry)

    # ─────────────────────────────────────────────────────
    #  QR generation
    # ─────────────────────────────────────────────────────
    def generate(self):
        inputs = [e.text() for e in self.current_entries]
        mode = self.combo_mode.currentText()
        grad = self.combo_grad.currentText()

        data_str = self.logic.format_data(mode, inputs)
        pil_img = self.logic.generate_image(data_str, grad, self.colors)

        im_data = pil_img.convert("RGBA").tobytes("raw", "RGBA")
        qim = QImage(im_data, pil_img.size[0], pil_img.size[1], QImage.Format_RGBA8888)
        pix = QPixmap.fromImage(qim)

        self.preview_lbl.setPixmap(
            pix.scaled(240, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
