import platform
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QLineEdit, QPushButton,
                             QColorDialog, QScrollArea, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QPixmap, QImage, QIcon
from themes import THEMES
from engine import QrLogic, INPUT_MAP
from ui_components import CustomTitleBar, GlassPanel, PrimaryButton, FONT

# ── Windows acrylic blur ──────────────────────────────────
_BLUR_AVAILABLE = False
if platform.system() == "Windows":
    try:
        from BlurWindow.blurWindow import GlobalBlur
        _BLUR_AVAILABLE = True
    except ImportError:
        pass


class GalaxyWindow(QMainWindow):
    def __init__(self, theme_key):
        super().__init__()
        self.theme = THEMES.get(theme_key, THEMES["apple-dark"])
        self.theme_key = theme_key
        self.logic = QrLogic()
        self.colors = [QColor("#ffffff"), QColor("#00f260"), QColor("#0575e6")]

        # Set official app icon
        icon_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '..',
                'assets',
                'icon.ico'))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(900, 600)  # Classic 3:2 landscape

        # Activate Windows Acrylic effect if available
        if _BLUR_AVAILABLE:
            GlobalBlur(self.winId(), Dark=True, Acrylic=True)

        # ── Desktop Window Background ────────────────────
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("CentralWidget")

        bg_hex = self.theme.get("bg", "#121219")
        bg_rgba = "rgba(30, 30, 35, 0.45)"  # fallback
        if bg_hex.startswith("#") and len(bg_hex) == 7:
            r, g, b = int(bg_hex[1:3], 16), int(
                bg_hex[3:5], 16), int(bg_hex[5:7], 16)
            bg_rgba = f"rgba({r}, {g}, {b}, 0.55)"

        # This acts as the translucent tint layer that the OS blur renders
        # behind
        self.central_widget.setStyleSheet(f"""
            QWidget#CentralWidget {{
                background-color: {bg_rgba};
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
        """)
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # ── Title bar ────────────────────────────────────
        self.title_bar = CustomTitleBar(self, self.theme_key)
        self.main_layout.addWidget(self.title_bar)

        # ── Content Layout ───────────────────────────────
        self.content_h_layout = QHBoxLayout()
        self.content_h_layout.setContentsMargins(24, 16, 24, 28)
        self.content_h_layout.setSpacing(16)
        self.main_layout.addLayout(self.content_h_layout)

        # ── Panel 1 (Left): Configuration ────────────────
        self.left_panel = GlassPanel(self.theme, self)
        self.left_panel.setMinimumWidth(320)
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(24, 24, 24, 24)
        self.left_layout.setSpacing(12)
        self._build_left_panel()

        # ── Panel 2 (Right): Output & Action ─────────────
        self.right_panel = GlassPanel(self.theme, self)
        self.right_panel.setMinimumWidth(360)
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(32, 32, 32, 32)
        self.right_layout.setSpacing(24)
        self._build_right_panel()

        self.content_h_layout.addWidget(self.left_panel, 40)
        self.content_h_layout.addWidget(self.right_panel, 60)

        self.update_inputs()

    # ─────────────────────────────────────────────────────
    #  Left Panel: Core Controls & Dynamic Inputs
    # ─────────────────────────────────────────────────────
    def _build_left_panel(self):
        # Header
        lbl_head = QLabel("Configuration")
        lbl_head.setStyleSheet(f"""
            color: rgba(255, 255, 255, 0.9);
            font-size: 16px;
            font-weight: 700;
            font-family: {FONT};
            letter-spacing: -0.3px;
        """)
        self.left_layout.addWidget(lbl_head)
        self.left_layout.addSpacing(8)

        # Protocol
        self.left_layout.addWidget(self._section_label("Data Protocol"))
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(INPUT_MAP.keys())
        self.combo_mode.setStyleSheet(self._combo_style())
        self.combo_mode.setFixedHeight(30)
        self.combo_mode.currentIndexChanged.connect(self.update_inputs)
        self.left_layout.addWidget(self.combo_mode)

        self.left_layout.addSpacing(6)

        # Gradient
        self.left_layout.addWidget(self._section_label("Gradient Engine"))
        self.combo_grad = QComboBox()
        self.combo_grad.addItems(
            ["Radial", "Vertical", "Horizontal", "Square"])
        self.combo_grad.setStyleSheet(self._combo_style())
        self.combo_grad.setFixedHeight(30)
        self.left_layout.addWidget(self.combo_grad)

        self.left_layout.addSpacing(6)

        # Visual Palette
        self.left_layout.addWidget(self._section_label("Visual Spectrum"))
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.btn_bg = self._make_color_swatch(0, "BG")
        self.btn_c = self._make_color_swatch(1, "Core")
        self.btn_e = self._make_color_swatch(2, "Edge")

        # Layout matching Apple style round chips
        btn_row.addWidget(self.btn_bg)
        btn_row.addWidget(self.btn_c)
        btn_row.addWidget(self.btn_e)
        btn_row.addStretch()
        self.left_layout.addLayout(btn_row)

        self.left_layout.addSpacing(8)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("border-bottom: 1px solid rgba(255,255,255,0.06);")
        self.left_layout.addWidget(line)
        self.left_layout.addSpacing(2)

        # Dynamic Input Holder
        self.input_widget = QWidget()
        self.input_widget.setStyleSheet("background: transparent;")
        self.input_layout = QVBoxLayout(self.input_widget)
        self.input_layout.setContentsMargins(0, 0, 0, 0)
        self.input_layout.setSpacing(8)
        self.input_layout.setAlignment(Qt.AlignTop)

        # Scroll area for many inputs
        self.input_scroll = QScrollArea()
        self.input_scroll.setWidgetResizable(True)
        self.input_scroll.setWidget(self.input_widget)
        self.input_scroll.viewport().setStyleSheet("background: transparent;")
        self.input_scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { width: 4px; background: transparent; }
            QScrollBar::handle:vertical { background: rgba(255,255,255,0.2); border-radius: 2px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        self.left_layout.addWidget(self.input_scroll)

    # ─────────────────────────────────────────────────────
    #  Right Panel: Clean Preview & Generate
    # ─────────────────────────────────────────────────────
    def _build_right_panel(self):
        from PyQt5.QtWidgets import QSizePolicy

        # Expanded preview to fill the full boxed space
        self.preview_lbl = QLabel()
        self.preview_lbl.setAlignment(Qt.AlignCenter)
        self.preview_lbl.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preview_lbl.setMinimumSize(250, 250)
        self.preview_lbl.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 0.15);
                border: 1px solid rgba(0, 0, 0, 0.4);
                border-top: 1px solid rgba(0, 0, 0, 0.7);
                border-bottom: 1px solid rgba(255, 255, 255, 0.08); /* inner reflection */
                border-radius: 12px;
            }
        """)

        # Insert directly to act as an expanding cell
        self.right_layout.addWidget(self.preview_lbl, 1)

        # Premium button
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_gen = PrimaryButton("Generate QR Code", self.theme, self)
        self.btn_gen.setMinimumWidth(160)
        self.btn_gen.clicked.connect(self.generate)
        btn_row.addWidget(self.btn_gen)
        btn_row.addStretch()

        self.right_layout.addLayout(btn_row)

    # ─────────────────────────────────────────────────────
    #  Styling & Logic
    # ─────────────────────────────────────────────────────
    def _section_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"""
            color: rgba(255, 255, 255, 0.5);
            font-size: 11px;
            font-weight: 600;
            font-family: {FONT};
            text-transform: uppercase;
            letter-spacing: 0.8px;
        """)
        return lbl

    def _combo_style(self):
        hover_col = "rgba(0, 0, 0, 0.3)"

        # Get theme accent specifically for focus/selection highlighting
        accent = self.theme.get("accent_grad", "#0A84FF")
        if "qlineargradient" in accent:
            # Fallback since you can't border-solid a linear grad directly
            # easily
            accent_border = "#0A84FF"
            if "stop:1 " in accent:
                accent_border = accent.split("stop:1 ")[1][:7]
        else:
            accent_border = accent

        return f"""
            QComboBox {{
                background-color: rgba(0, 0, 0, 0.2);
                border: 1px solid rgba(0, 0, 0, 0.4);
                border-top: 1px solid rgba(0, 0, 0, 0.6);
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                color: rgba(255,255,255, 0.9);
                padding: 0px 8px;
                border-radius: 6px;
                font-family: {FONT};
                font-size: 13px;
            }}
            QComboBox:hover {{
                background-color: {hover_col};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox::down-arrow {{
                image: none;
                width: 0;
            }}
            QComboBox QAbstractItemView {{
                background-color: rgba(35, 35, 40, 0.98);
                border: 1px solid rgba(0, 0, 0, 0.8);
                border-radius: 8px;
                color: white;
                selection-background-color: {accent_border};
                padding: 4px;
                outline: 0;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 4px 8px;
                border-radius: 4px;
                min-height: 22px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {accent_border};
            }}
        """

    def _input_style(self):
        accent = self.theme.get("accent_grad", "#0A84FF")
        if "qlineargradient" in accent:
            if "stop:1 " in accent:
                accent = accent.split("stop:1 ")[1][:7]
            else:
                accent = "#0A84FF"

        return f"""
            QLineEdit {{
                background-color: rgba(0, 0, 0, 0.2);
                border: 1px solid rgba(0, 0, 0, 0.4);
                border-top: 1px solid rgba(0, 0, 0, 0.6);
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                color: rgba(255,255,255, 0.9);
                padding: 4px 10px;
                border-radius: 6px;
                font-family: {FONT};
                font-size: 13px;
                selection-background-color: {accent};
            }}
            QLineEdit:hover {{
                background-color: rgba(0, 0, 0, 0.3);
            }}
            QLineEdit:focus {{
                border: 2px solid {accent};
                background-color: rgba(0, 0, 0, 0.1);
                padding: 3px 9px;
            }}
            QLineEdit::placeholder {{
                color: rgba(255, 255, 255, 0.3);
            }}
        """

    def _make_color_swatch(self, idx, tooltip):
        btn = QPushButton()
        btn.setFixedSize(28, 28)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(f"{tooltip} Color")
        self._apply_color_btn_style(btn, self.colors[idx])
        btn.clicked.connect(lambda _, b=btn, i=idx: self._pick_color(i, b))
        return btn

    def _apply_color_btn_style(self, btn, color):
        if isinstance(color, QColor):
            r, g, b = color.red(), color.green(), color.blue()
        else:
            hex_col = str(color)
            r, g, b = int(hex_col[1:3], 16), int(
                hex_col[3:5], 16), int(hex_col[5:7], 16)

        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba({r}, {g}, {b}, 1.0);
                border: 1px solid rgba(0, 0, 0, 0.3);
                border-top: 1px solid rgba(255, 255, 255, 0.4);
                border-bottom: 1px solid rgba(0, 0, 0, 0.6);
                border-radius: 14px; /* Perfectly circular */
            }}
            QPushButton:hover {{
                border: 2px solid rgba(255, 255, 255, 0.6);
            }}
            QPushButton:pressed {{
                background-color: rgba({r}, {g}, {b}, 0.8);
            }}
        """)

    def _pick_color(self, idx, btn):
        dialog = QColorDialog(self.colors[idx], self)

        # Add Apple macOS specific dialog styling properties if possible
        dialog.setOption(QColorDialog.ShowAlphaChannel, False)
        dialog.setOption(
            QColorDialog.DontUseNativeDialog,
            False)  # Let OS render the color wheel

        if dialog.exec_() == QColorDialog.Accepted:
            c = dialog.selectedColor()
            self.colors[idx] = c
            self._apply_color_btn_style(btn, c)

    def update_inputs(self):
        # Clear specific inputs
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
            row.setContentsMargins(0, 0, 0, 0)

            lbl = QLabel(f)
            lbl.setStyleSheet(f"""
                color: rgba(255, 255, 255, 0.75);
                font-size: 12px;
                font-weight: 500;
                font-family: {FONT};
                letter-spacing: 0.2px;
                padding-top: 6px;
            """)
            row.addWidget(lbl)

            entry = QLineEdit()
            entry.setPlaceholderText(f"Paste {f}...")
            entry.setFixedHeight(30)
            entry.setStyleSheet(self._input_style())
            row.addWidget(entry)

            self.input_layout.addLayout(row)
            self.current_entries.append(entry)

        self.input_layout.addStretch()

    def generate(self):
        inputs = [e.text() for e in self.current_entries]
        mode = self.combo_mode.currentText()
        grad = self.combo_grad.currentText()

        data_str = self.logic.format_data(mode, inputs)
        pil_img = self.logic.generate_image(data_str, grad, self.colors)

        im_data = pil_img.convert("RGBA").tobytes("raw", "RGBA")
        qim = QImage(
            im_data,
            pil_img.size[0],
            pil_img.size[1],
            QImage.Format_RGBA8888)
        pix = QPixmap.fromImage(qim)

        sz = min(self.preview_lbl.width(), self.preview_lbl.height()) - 30
        if sz < 150:
            sz = 240

        self.preview_lbl.setPixmap(
            pix.scaled(sz, sz, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
