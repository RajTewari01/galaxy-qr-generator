import sys
import argparse
from PyQt5.QtWidgets import QApplication
from themes import THEMES
from runner import GalaxyWindow


def main():
    parser = argparse.ArgumentParser(description='Galaxy QR Core Engine')
    parser.add_argument(
        '--theme',
        type=str,
        default='apple-dark',
        choices=THEMES.keys(),
        help='Initialize the runner with a specific styling theme'
    )
    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = GalaxyWindow(args.theme)
    # Center Window on primary display
    screen_rect = app.primaryScreen().geometry()
    window_rect = window.geometry()
    window.move(
        (screen_rect.width() - window_rect.width()) // 2,
        (screen_rect.height() - window_rect.height()) // 2
    )
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
