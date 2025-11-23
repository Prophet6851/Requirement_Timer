# main.py

import os
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from db.database import init_db
from ui.main_window import MainWindow


def main():
    # 初始化数据库
    init_db()

    app = QApplication(sys.argv)

    # 设置窗口图标（如果存在）
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
