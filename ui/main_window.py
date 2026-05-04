from datetime import datetime, date
from typing import Optional

import sys
import os

# 如果直接运行此文件，将父目录加入路径以支持导入
if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QSizePolicy, QMessageBox, QDialog, QFormLayout,
    QLineEdit, QComboBox, QDateEdit, QTextEdit,
    QDialogButtonBox, QStyledItemDelegate, QProgressBar, QTabWidget, QTextBrowser, QStackedWidget, QScrollArea, QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QDate, QRect, QPropertyAnimation, QEasingCurve, QMimeData, QPoint
from PySide6.QtGui import QColor, QPainter, QDrag

from models.task import Task

try:
    from .calendar_view import CalendarDialog
    from .dashboard_view import DashboardDialog
except ImportError:
    from ui.calendar_view import CalendarDialog
    from ui.dashboard_view import DashboardDialog

from utils.maxims import get_random_maxim  # 新增：导入语录工具
# 引入 XP 相关数据库操作
from db.task_repository import get_xp, add_xp, get_level

GLOBAL_QSS = """
* { 
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; 
    outline: none; 
}
QMainWindow, QDialog, QWidget#kanban_widget { background: #FFFFFF; }
QFrame#sidebar { background: #F5F5F7; border-right: 1px solid #E5E5EA; }
QWidget#contentArea { background: #FFFFFF; }
QLabel#appTitle { font-size: 22px; font-weight: 800; color: #111111; padding-bottom: 10px; }
QLabel#pageTitle { font-size: 24px; font-weight: 700; color: #1C1C1E; }
QPushButton#navButton { text-align: left; padding: 10px 14px; border-radius: 8px; font-size: 14px; font-weight: 600; color: #3A3A3C; background: transparent; border: none; margin-bottom: 4px; }
QPushButton#navButton:hover { background: #EBEBF0; }
QPushButton#navButton:checked { background: #E5F1FF; color: #007AFF; }

/* ======== Modern Inputs ======== */
QLineEdit, QTextEdit, QTextBrowser { 
    background: #F2F2F7; border: 1px solid transparent; border-radius: 8px; 
    padding: 8px 12px; font-size: 13px; color: #1C1C1E; 
    selection-background-color: #007AFF; selection-color: #FFFFFF; 
}
QLineEdit:hover, QTextEdit:hover { background: #EBEBF0; border: 1px solid transparent; }
QLineEdit:focus, QTextEdit:focus { background: #FFFFFF; border: 1px solid #007AFF; }

/* ======== ComboBoxes & DateEdits (Dropdowns) ======== */
QComboBox, QDateEdit { 
    background: #F2F2F7; border: 1px solid transparent; border-radius: 8px; 
    padding: 8px 24px 8px 12px; /* Reduce right padding to avoid clipping text */
    font-size: 13px; color: #1C1C1E; 
}
QComboBox:hover, QDateEdit:hover { background: #EBEBF0; border: 1px solid transparent; }
QComboBox:focus, QDateEdit:focus { background: #FFFFFF; border: 1px solid #007AFF; }

QComboBox::drop-down, QDateEdit::drop-down { 
    subcontrol-origin: padding; subcontrol-position: center right; 
    width: 24px; border-left: none; background: transparent; 
}
/* 绘制独立向下的 SVG 箭头 */
QComboBox::down-arrow { 
    image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%238E8E93' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><polyline points='6 9 12 15 18 9'></polyline></svg>");
    width: 16px; height: 16px;
}
/* 日期控件的下拉绘制一个日历 Icon */
QDateEdit::down-arrow {
    image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%238E8E93' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><rect x='3' y='4' width='18' height='18' rx='2' ry='2'></rect><line x1='16' y1='2' x2='16' y2='6'></line><line x1='8' y1='2' x2='8' y2='6'></line><line x1='3' y1='10' x2='21' y2='10'></line></svg>");
    width: 16px; height: 16px;
}

QComboBox QAbstractItemView { 
    background: #FFFFFF; border: 1px solid #E5E5EA; border-radius: 8px; 
    selection-background-color: #F2F2F7; selection-color: #007AFF; outline: none; padding: 4px; 
}
QComboBox QAbstractItemView::item { min-height: 36px; border-radius: 6px; padding: 6px 12px; color: #1C1C1E; }
QComboBox QAbstractItemView::item:hover, QComboBox QAbstractItemView::item:selected { 
    background-color: #E5F1FF; color: #007AFF; font-weight: bold; 
}

/* ======== Calendar Popup ======== */
QCalendarWidget QWidget#qt_calendar_navigationbar { background-color: #F5F5F7; border-bottom: 1px solid #E5E5EA; min-height: 35px; }
QCalendarWidget QToolButton { color: #1C1C1E; font-weight: 600; background: transparent; border-radius: 6px; padding: 4px 8px; }
QCalendarWidget QToolButton:hover { background-color: #E5E5EA; }
QCalendarWidget QMenu { background-color: #FFFFFF; border: 1px solid #E5E5EA; border-radius: 8px; }
QCalendarWidget QSpinBox { background: transparent; border: none; }
QCalendarWidget QAbstractItemView:enabled { background-color: #FFFFFF; selection-background-color: #007AFF; selection-color: #FFFFFF; }
QCalendarWidget QAbstractItemView:disabled { color: #C7C7CC; }

/* ======== Buttons ======== */
QPushButton { 
    border-radius: 8px; padding: 8px 18px; background: #FFFFFF; color: #1C1C1E; 
    font-size: 13px; font-weight: 600; border: 1px solid #E5E5EA; 
}
QPushButton:hover { background: #F2F2F7; border-color: #D1D1D6; color: #111111; }
QPushButton:pressed { background: #E5E5EA; }
QPushButton#primaryButton { background: #007AFF; color: #FFFFFF; border: none; }
QPushButton#primaryButton:hover { background: #0066D6; }
QPushButton#primaryButton:pressed { background: #0052B3; }
QPushButton#dangerButton { background: #FF3B30; color: #FFFFFF; border: none; }
QPushButton#dangerButton:hover { background: #E0352B; }
QPushButton#dangerButton:pressed { background: #B22822; }

/* ======== Table ======== */
QTableWidget { 
    background: #FFFFFF; border: 1px solid #E5E5EA; border-radius: 12px; 
    gridline-color: transparent; alternate-background-color: #FAFAFC; 
    selection-background-color: #F5F5F7; selection-color: #000000; outline: none; 
}
QTableWidget::item { border-bottom: 1px solid #F5F5F7; padding: 8px 4px; }
QHeaderView { background: transparent; }
QHeaderView::section { 
    background: #FFFFFF; padding: 12px 8px; border: none; 
    border-bottom: 1px solid #E5E5EA; font-weight: 600; color: #8E8E93; font-size: 12px; 
}

/* ======== Progress Bar ======== */
QProgressBar { border: none; border-radius: 6px; background: #E5E5EA; text-align: center; color: #1C1C1E; font-size: 10px; font-weight: bold; }
QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #007AFF, stop:1 #34C759); border-radius: 6px; }
QProgressBar#xpBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFD60A, stop:1 #FF9500); }

/* ======== Form Layout in Dialogs ======== */
QFormLayout { spacing: 16px; }

/* ======== Scrollbars ======== */
QScrollBar:vertical, QScrollBar:horizontal { 
    border: none; background: transparent; width: 12px; height: 12px; 
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal { 
    background: #D1D1D6; border-radius: 6px; min-height: 24px; min-width: 24px; margin: 2px;
}
QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover { background: #AEAEB2; }
QScrollBar::add-line, QScrollBar::sub-line, QScrollBar::add-page, QScrollBar::sub-page { border: none; background: none; }

/* ======== Tabs ======== */
QTabWidget::pane { border: none; background: transparent; margin-top: 8px; }
QTabBar { outline: none; }
QTabBar::tab { 
    background: #F2F2F7; color: #8E8E93; padding: 8px 24px; 
    border-radius: 8px; margin-right: 8px; font-weight: 600; font-size: 13px; border: none; 
}
QTabBar::tab:hover { background: #E5E5EA; color: #1C1C1E; }
QTabBar::tab:selected { background: #007AFF; color: #FFFFFF; }

/* ======== ToolTip ======== */
QToolTip { background: #1C1C1E; color: #FFFFFF; border: none; border-radius: 6px; padding: 6px 10px; font-size: 12px; font-weight: 500; }
"""

config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
try:
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)
        STATUS_OPTIONS = config_data.get("STATUS_OPTIONS", [])
        PRIORITY_OPTIONS = config_data.get("PRIORITY_OPTIONS", [])
        COMPLETED_STATUSES = config_data.get("COMPLETED_STATUSES", [])
        XP_MAP = config_data.get("XP_MAP", {})
except Exception as e:
    # 状态、优先级配置
    STATUS_OPTIONS = [
        "策划中",
        "交互案",
        "美术",
        "开发中",
        "待验收",
        "验收完",
        "测试回归bug",
        "已上线（归档）",
    ]

    PRIORITY_OPTIONS = ["高", "中", "低"]

    # 这些状态都视为“已完成”
    COMPLETED_STATUSES = ["验收完", "测试回归bug", "已上线（归档）"]
    XP_MAP = {
        "高": 100,
        "中": 50,
        "低": 20
    }

class ProgressDelegate(QStyledItemDelegate):
    """表格里显示扁平进度条（Apple 风格：浅灰底 + 蓝色条 + 白字）"""

    def paint(self, painter, option, index):
        value_str = index.data()
        try:
            value = float(value_str)
        except (TypeError, ValueError):
            super().paint(painter, option, index)
            return

        progress = max(0, min(100, int(round(value))))
        rect: QRect = option.rect.adjusted(6, 6, -6, -6)

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        # 背景条
        bg_color = QColor("#E5E5EA")
        painter.setPen(Qt.NoPen)
        painter.setBrush(bg_color)
        radius = rect.height() / 2
        painter.drawRoundedRect(rect, radius, radius)

        # 前景条
        if progress > 0:
            fill_width = int(rect.width() * progress / 100)
            fill_rect = QRect(rect.left(), rect.top(), fill_width, rect.height())
            fg_color = QColor("#007AFF")
            painter.setBrush(fg_color)
            painter.drawRoundedRect(fill_rect, radius, radius)

        # 文字
        if progress > 0:
            text_color = QColor("#FFFFFF") if progress >= 25 else QColor("#1C1C1E")
        else:
            text_color = QColor("#8E8E93")

        painter.setPen(text_color)
        font = painter.font()
        font.setPointSize(font.pointSize() - 1)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, f"{progress}%")

        painter.restore()


class TaskDialog(QDialog):
    """新建/编辑任务"""

    def __init__(self, parent=None, task: Optional[Task] = None):
        super().__init__(parent)
        self.setWindowTitle("编辑需求" if task and task.id is not None else "新建需求")
        self.setModal(True)
        self.task_id = task.id if task else None

        self._build_ui()
        if task:
            self._fill_from_task(task)

    def _build_ui(self):
        self.setMinimumWidth(500)
        self.setStyleSheet(GLOBAL_QSS)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(10)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignTop)
        form.setVerticalSpacing(8)

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("例如：优化xxxx工作项 v2")
        form.addRow("标题：", self.title_edit)

        self.module_edit = QLineEdit()
        self.module_edit.setPlaceholderText("例如：AI / 系统 / 数值 / 关卡")
        form.addRow("模块：", self.module_edit)

        self.version_edit = QLineEdit()
        self.version_edit.setPlaceholderText("例如：v2.3.0 国服")
        form.addRow("版本号：", self.version_edit)

        self.status_combo = QComboBox()
        self.status_combo.addItems(STATUS_OPTIONS)
        form.addRow("状态：", self.status_combo)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(PRIORITY_OPTIONS)
        self.priority_combo.setCurrentIndex(1)
        form.addRow("优先级：", self.priority_combo)

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.setDate(QDate.currentDate())
        form.addRow("开始日期：", self.start_date_edit)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.setDate(QDate.currentDate())
        form.addRow("截止日期：", self.end_date_edit)

        self.notes_tabs = QTabWidget()
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("备注：支持 Markdown 格式，记录依赖项、沟通记录等……")

        self.notes_preview = QTextBrowser()
        self.notes_preview.setOpenExternalLinks(True)

        self.notes_tabs.addTab(self.notes_edit, "编辑")
        self.notes_tabs.addTab(self.notes_preview, "预览")
        self.notes_tabs.currentChanged.connect(self._update_markdown_preview)

        self.notes_tabs.setFixedHeight(150)
        form.addRow("备注：", self.notes_tabs)

        layout.addLayout(form)

        btn_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            orientation=Qt.Horizontal,
            parent=self,
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def _fill_from_task(self, task: Task):
        self.title_edit.setText(task.title or "")
        self.module_edit.setText(task.module or "")
        self.version_edit.setText(task.version or "")
        self.status_combo.setCurrentText(task.status or STATUS_OPTIONS[0])
        self.priority_combo.setCurrentText(task.priority or PRIORITY_OPTIONS[1])

        self._set_date_safe(self.start_date_edit, task.plan_start)
        self._set_date_safe(self.end_date_edit, task.plan_end)
        self.notes_edit.setPlainText(task.notes or "")
        self._update_markdown_preview(0)

    def _update_markdown_preview(self, index):
        if index == 1:
            try:
                import markdown
                text = self.notes_edit.toPlainText()
                html = markdown.markdown(text, extensions=['tables', 'fenced_code'])
                self.notes_preview.setHtml(html)
            except ImportError:
                self.notes_preview.setHtml("<p><i>未安装 markdown 库，无法预览。</i></p>" + self.notes_edit.toPlainText().replace('\n', '<br>'))

    @staticmethod
    def _set_date_safe(widget: QDateEdit, s: str):
        try:
            y, m, d = map(int, s.split("-"))
            widget.setDate(QDate(y, m, d))
        except Exception:
            pass

    def accept(self):
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "提示", "标题不能为空。")
            return
        super().accept()

    def get_task(self) -> Task:
        return Task(
            id=self.task_id,
            title=self.title_edit.text().strip(),
            module=self.module_edit.text().strip(),
            version=self.version_edit.text().strip(),
            status=self.status_combo.currentText(),
            priority=self.priority_combo.currentText(),
            plan_start=self.start_date_edit.date().toString("yyyy-MM-dd"),
            plan_end=self.end_date_edit.date().toString("yyyy-MM-dd"),
            notes=self.notes_edit.toPlainText().strip(),
        )


class ArchiveDialog(QDialog):
    """归档页面：显示已上线（归档）任务，并支持 移出归档 / 删除"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("归档 - 已上线需求")
        self.resize(900, 540)
        self.tasks: list[Task] = []
        self._build_ui()
        self.load_archived_tasks()

    def _build_ui(self):
        self.setStyleSheet(GLOBAL_QSS)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QLabel("已上线需求归档")
        header.setStyleSheet("font-size: 14px; font-weight: 600; color: #111111;")
        layout.addWidget(header)

        # 表格：带备注列
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "标题", "模块", "版本", "状态", "优先级",
            "开始日期", "截止日期",
            "已推进天数", "剩余天数", "备注", "进度",
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.verticalHeader().setDefaultSectionSize(26)
        self.table.setItemDelegateForColumn(10, ProgressDelegate(self.table))

        layout.addWidget(self.table)

        # 按钮区域：移出归档 / 删除 / 关闭
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.unarchive_btn = QPushButton("移出归档")
        self.unarchive_btn.setObjectName("primaryButton")

        self.delete_btn = QPushButton("删除")
        self.delete_btn.setObjectName("dangerButton")

        close_btn = QPushButton("关闭")

        btn_layout.addWidget(self.unarchive_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

        # 信号
        self.unarchive_btn.clicked.connect(self.unarchive_task)
        self.delete_btn.clicked.connect(self.delete_task)
        close_btn.clicked.connect(self.accept)

    def load_archived_tasks(self):
        from db.task_repository import list_tasks

        all_tasks = list_tasks()
        self.tasks = [t for t in all_tasks if t.status == "已上线（归档）"]

        self.table.setRowCount(len(self.tasks))
        today = date.today()

        for row_idx, task in enumerate(self.tasks):
            spent, _ = MainWindow.calculate_days(task.plan_start, task.plan_end, today)
            progress = 100.0
            left_display = "已完成"

            values = [
                task.title,
                task.module,
                task.version,
                task.status,
                task.priority,
                task.plan_start,
                task.plan_end,
                str(spent) if spent != "" else "",
                left_display,
                task.notes or "",
                f"{progress:.0f}",
            ]

            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                # 剩余天数列：已完成 → 绿色
                if col == 8:
                    item.setForeground(QColor("#34C759"))
                self.table.setItem(row_idx, col, item)

        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(10, 140)  # 进度列宽

    def _get_selected_task(self) -> Optional[Task]:
        row = self.table.currentRow()
        if row < 0 or row >= len(self.tasks):
            return None
        return self.tasks[row]

    def unarchive_task(self):
        """将任务从归档恢复（默认改为 '待验收'）"""
        task = self._get_selected_task()
        if not task:
            QMessageBox.information(self, "提示", "请先选中要移出的任务。")
            return

        reply = QMessageBox.question(
            self,
            "确认移出归档",
            f"将【{task.title}】移出归档并恢复为『待验收』？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        from db.task_repository import update_task_status

        update_task_status(task.id, "待验收")
        QMessageBox.information(self, "成功", "已移出归档。")
        self.load_archived_tasks()

    def delete_task(self):
        """删除归档中的任务"""
        task = self._get_selected_task()
        if not task:
            QMessageBox.information(self, "提示", "请先选中要删除的任务。")
            return

        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除【{task.title}】吗？此操作不可恢复。",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        from db.task_repository import delete_task
        delete_task(task.id)
        QMessageBox.information(self, "成功", "任务已删除。")
        self.load_archived_tasks()


class MainWindow(QMainWindow):
    def show_about(self):
        """关于弹窗：显示版本号和制作人"""
        QMessageBox.information(
            self,
            "关于 Requirement Timer",
            "Requirement Timer\n"
            "版本：v1.2\n"
            "制作人：崔\n\n"
            "一个为策划制作的需求管理工具，基于 Python + PySide6 + SQLite 开发，"
            "帮你把策划需求推进节奏一眼看清。",
        )

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Requirement Timer - 需求时间管理")
        self.resize(1200, 750)

        self.tasks: list[Task] = []

        self._build_ui()
        self.load_tasks()
        self.refresh_xp_display()  # 初始化 XP 显示

    # ============ UI ============

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        self.setStyleSheet(GLOBAL_QSS)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ================= Sidebar =================
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(20, 30, 20, 24)
        sidebar_layout.setSpacing(8)

        app_title = QLabel("需求时间管理器")
        app_title.setObjectName("appTitle")
        sidebar_layout.addWidget(app_title)
        sidebar_layout.addSpacing(20)

        # Nav Buttons
        self.nav_list_btn = QPushButton("📋  任务列表")
        self.nav_kanban_btn = QPushButton("🗂️  敏捷看板")
        self.nav_dashboard_btn = QPushButton("📊  统计仪表盘")
        self.nav_calendar_btn = QPushButton("📅  日历视图")
        self.nav_archive_btn = QPushButton("📦  项目归档")

        self.nav_buttons = [
            self.nav_list_btn, self.nav_kanban_btn,
            self.nav_dashboard_btn, self.nav_calendar_btn, self.nav_archive_btn
        ]

        for i, btn in enumerate(self.nav_buttons):
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            # Connect using closure inside lambda
            btn.clicked.connect(lambda checked, idx=i: self.switch_nav(idx))
            sidebar_layout.addWidget(btn)

        self.nav_list_btn.setChecked(True)

        sidebar_layout.addStretch()

        # Levels and XP in Sidebar
        xp_container = QFrame()
        xp_container.setStyleSheet("background: #FFFFFF; border-radius: 12px; padding: 12px;")
        xp_layout = QVBoxLayout(xp_container)
        xp_layout.setContentsMargins(0,0,0,0)

        level_header_layout = QHBoxLayout()
        lvl_title = QLabel("项目成长")
        lvl_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #8E8E93;")
        self.level_label = QLabel("Lv.1")
        self.level_label.setStyleSheet("color: #FF9500; font-weight: 800; font-size: 14px;")
        level_header_layout.addWidget(lvl_title)
        level_header_layout.addStretch()
        level_header_layout.addWidget(self.level_label)

        self.xp_bar = QProgressBar()
        self.xp_bar.setObjectName("xpBar")
        self.xp_bar.setRange(0, 1000)
        self.xp_bar.setTextVisible(False)
        self.xp_bar.setFixedHeight(12)

        self.xp_text = QLabel("0 / 1000 XP")
        self.xp_text.setAlignment(Qt.AlignCenter)
        self.xp_text.setStyleSheet("font-size: 10px; color: #8E8E93; margin-top: 4px;")

        xp_layout.addLayout(level_header_layout)
        xp_layout.addWidget(self.xp_bar)
        xp_layout.addWidget(self.xp_text)

        sidebar_layout.addWidget(xp_container)

        # Bottom tools
        self.about_btn = QPushButton("ℹ️ 关于软件")
        self.about_btn.setObjectName("navButton")
        self.about_btn.clicked.connect(self.show_about)
        sidebar_layout.addWidget(self.about_btn)

        main_layout.addWidget(self.sidebar)

        # ================= Content Area =================
        self.content_area = QWidget()
        self.content_area.setObjectName("contentArea")
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(32, 28, 32, 24)
        content_layout.setSpacing(20)

        # Top Bar
        top_bar_layout = QHBoxLayout()

        self.page_title = QLabel("任务列表")
        self.page_title.setObjectName("pageTitle")
        top_bar_layout.addWidget(self.page_title)

        self.summary_label = QLabel("当前任务：0 / 归档：0")
        self.summary_label.setStyleSheet("color: #8E8E93; font-size: 12px; font-weight: 500; margin-left: 10px;")
        top_bar_layout.addWidget(self.summary_label)

        top_bar_layout.addStretch()

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 搜索任务...")
        self.search_edit.setFixedWidth(200)

        self.status_filter = QComboBox()
        self.status_filter.addItem("全部状态")
        for s in STATUS_OPTIONS:
            if s != "已上线（归档）":
                self.status_filter.addItem(s)
        self.status_filter.setFixedWidth(150)

        self.priority_filter = QComboBox()
        self.priority_filter.addItem("全部优先级")
        self.priority_filter.addItems(PRIORITY_OPTIONS)
        self.priority_filter.setFixedWidth(140)

        self.new_btn = QPushButton("➕ 新建任务")
        self.new_btn.setObjectName("primaryButton")
        self.new_btn.setFixedWidth(120)

        top_bar_layout.addWidget(self.search_edit)
        top_bar_layout.addWidget(self.status_filter)
        top_bar_layout.addWidget(self.priority_filter)
        top_bar_layout.addSpacing(16)
        top_bar_layout.addWidget(self.new_btn)

        content_layout.addLayout(top_bar_layout)

        # Stacked Widget (List vs Kanban)
        self.stacked_widget = QStackedWidget()

        # View 0: Table
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0,0,0,0)
        table_layout.setSpacing(12)

        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "标题", "模块", "版本", "状态", "优先级",
            "开始日期", "截止日期",
            "推进", "剩余天数", "备注", "进度",
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setSortingEnabled(False)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setItemDelegateForColumn(10, ProgressDelegate(self.table))
        self.table.horizontalHeader().setStretchLastSection(True)

        # Table Action tools
        table_actions_layout = QHBoxLayout()
        self.edit_btn = QPushButton("✏️ 编辑选中")
        self.delete_btn = QPushButton("🗑️ 删除")
        self.delete_btn.setObjectName("dangerButton")
        self.refresh_btn = QPushButton("🔄 刷新")
        self.export_btn = QPushButton("📤 导出 CSV")

        table_actions_layout.addWidget(self.edit_btn)
        table_actions_layout.addWidget(self.delete_btn)
        table_actions_layout.addWidget(self.refresh_btn)
        table_actions_layout.addStretch()
        table_actions_layout.addWidget(self.export_btn)

        table_layout.addWidget(self.table)
        table_layout.addLayout(table_actions_layout)

        self.stacked_widget.addWidget(table_container)  # Index 0

        # View 1: Kanban View Placeholder
        self.kanban_widget = QWidget()
        self.kanban_widget.setObjectName("kanban_widget")
        self.kanban_layout = QHBoxLayout(self.kanban_widget)
        self.kanban_layout.setAlignment(Qt.AlignLeft)

        self.kanban_scroll = QScrollArea()
        self.kanban_scroll.setWidgetResizable(True)
        self.kanban_scroll.setWidget(self.kanban_widget)
        self.kanban_scroll.setObjectName("kanban_scroll")

        self.stacked_widget.addWidget(self.kanban_scroll) # Index 1

        content_layout.addWidget(self.stacked_widget)

        # Maxim Footer
        self.maxim_label = QLabel()
        self.maxim_label.setAlignment(Qt.AlignCenter)
        self.maxim_label.setStyleSheet("""
            QLabel {
                color: #A1A1A6;
                font-size: 12px;
                font-weight: 500;
                margin-top: 10px;
            }
            QLabel:hover {
                color: #007AFF;
            }
        """)
        self.maxim_label.setToolTip("点击刷新灵感")
        self.maxim_label.mousePressEvent = self.refresh_maxim  # 绑定点击事件

        content_layout.addWidget(self.maxim_label)

        main_layout.addWidget(self.content_area)

        self.refresh_maxim(None) # 初始化显示

        # 信号
        self.new_btn.clicked.connect(self.new_task)
        self.edit_btn.clicked.connect(self.edit_task)
        self.delete_btn.clicked.connect(self.delete_task)
        self.refresh_btn.clicked.connect(self.load_tasks)
        self.export_btn.clicked.connect(self.export_to_csv)
        self.status_filter.currentIndexChanged.connect(self.load_tasks)
        self.priority_filter.currentIndexChanged.connect(self.load_tasks)
        self.search_edit.textChanged.connect(self.load_tasks)

    # ============ 导航逻辑 ============
    def switch_nav(self, index):
        # Prevent unchecking the activated item
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

        self.stacked_widget.setCurrentIndex(0) # Default jump back to table if needed

        if index == 0:
            self.page_title.setText("任务列表")
            self.stacked_widget.setCurrentIndex(0)
            self._set_filters_visible(True)
        elif index == 1:
            self.page_title.setText("敏捷看板")
            self.stacked_widget.setCurrentIndex(1)
            self._set_filters_visible(True)
        elif index == 2:
            self.open_dashboard()
            # restore nav state
            self.switch_nav(0)
        elif index == 3:
            self.open_calendar()
            self.switch_nav(0)
        elif index == 4:
            self.open_archive()
            self.switch_nav(0)

    def _set_filters_visible(self, visible: bool):
        self.search_edit.setVisible(visible)
        self.status_filter.setVisible(visible)
        self.priority_filter.setVisible(visible)

    # ============ 数据加载 ============
    def load_tasks(self):
        """当前页面：只显示 非 已上线（归档） 的任务；逾期/已完成显示规则更新"""
        from db.task_repository import list_tasks

        all_tasks = list_tasks()
        active_tasks = [t for t in all_tasks if t.status != "已上线（归档）"]
        archived_tasks = [t for t in all_tasks if t.status == "已上线（归档）"]

        status_f = self.status_filter.currentText()
        priority_f = self.priority_filter.currentText()
        search_text = self.search_edit.text().strip().lower()

        def match(task: Task) -> bool:
            if status_f != "全部" and task.status != status_f:
                return False
            if priority_f != "全部" and task.priority != priority_f:
                return False
            if search_text and search_text not in task.title.lower() and search_text not in (task.notes or "").lower():
                return False
            return True

        self.tasks = [t for t in active_tasks if match(t)]

        self.table.setRowCount(len(self.tasks))
        today = date.today()

        for row_idx, task in enumerate(self.tasks):
            spent, left = self.calculate_days(task.plan_start, task.plan_end, today)
            progress = self.calculate_progress(spent, left)

            # 对已完成状态，直接强制 100% 进度
            if task.status in COMPLETED_STATUSES:
                progress = 100.0

            # 剩余天数显示逻辑
            if task.status in COMPLETED_STATUSES:
                left_display = "已完成"
            else:
                if isinstance(left, int) and left < 0:
                    left_display = "已逾期"
                else:
                    left_display = str(left) if left != "" else ""

            values = [
                task.title,
                task.module,
                task.version,
                task.status,
                task.priority,
                task.plan_start,
                task.plan_end,
                str(spent) if spent != "" else "",
                left_display,
                task.notes or "",
                f"{progress:.0f}" if progress is not None else "",
            ]

            for col, val in enumerate(values):
                item = QTableWidgetItem(val)

                # 逾期高亮：仅当不是完成状态且 left < 0
                if (
                    col in (0, 8) and
                    isinstance(left, int) and left < 0 and
                    task.status not in COMPLETED_STATUSES
                ):
                    item.setForeground(QColor("#FF3B30"))  # Apple 红

                # 已完成：剩余天数列绿色
                if col == 8 and task.status in COMPLETED_STATUSES:
                    item.setForeground(QColor("#34C759"))  # Apple 绿

                self.table.setItem(row_idx, col, item)

        self.summary_label.setText(
            f"当前任务：{len(active_tasks)} / 归档：{len(archived_tasks)}"
        )
        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(10, 140)  # 进度条列宽
        self.update_kanban_view()

    def update_kanban_view(self):
        # 清除现有列
        for i in reversed(range(self.kanban_layout.count())):
            widget = self.kanban_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        columns = ["策划中", "开发中", "待验收", "验收完", "测试回归bug"]

        for col_status in columns:
            col_widget = QWidget()
            col_widget.setFixedWidth(280)
            col_widget.setStyleSheet("background: #F5F5F7; border-radius: 12px; margin-right: 12px;")
            col_v_layout = QVBoxLayout(col_widget)
            col_v_layout.setAlignment(Qt.AlignTop)
            col_v_layout.setContentsMargins(14, 16, 14, 16)
            col_v_layout.setSpacing(12)

            col_tasks = [t for t in self.tasks if t.status == col_status]

            # Header
            header_layout = QHBoxLayout()
            title_lbl = QLabel(col_status)
            title_lbl.setStyleSheet("font-weight: 700; font-size: 15px; color: #111111; border: none; background: transparent;")
            count_lbl = QLabel(str(len(col_tasks)))
            count_lbl.setStyleSheet("font-weight: 600; font-size: 12px; color: #8E8E93; background: #E5E5EA; padding: 2px 8px; border-radius: 10px;")

            header_layout.addWidget(title_lbl)
            header_layout.addStretch()
            header_layout.addWidget(count_lbl)
            col_v_layout.addLayout(header_layout)

            for t in col_tasks:
                card = QFrame()
                card.setStyleSheet("""
                    QFrame {
                        background: #FFFFFF;
                        border: 1px solid #E5E5EA;
                        border-radius: 10px;
                    }
                    QFrame:hover {
                        border: 1px solid #D1D1D6;
                    }
                """)

                shadow = QGraphicsDropShadowEffect()
                shadow.setBlurRadius(15)
                shadow.setColor(QColor(0, 0, 0, 10))
                shadow.setOffset(0, 4)
                card.setGraphicsEffect(shadow)

                clayout = QVBoxLayout(card)
                clayout.setContentsMargins(14, 14, 14, 14)
                clayout.setSpacing(8)

                t_lbl = QLabel(t.title)
                t_lbl.setWordWrap(True)
                t_lbl.setStyleSheet("font-weight: 600; font-size: 14px; color: #111111; background: transparent; border: none;")
                clayout.addWidget(t_lbl)

                desc_h_layout = QHBoxLayout()
                desc_h_layout.setSpacing(6)

                if t.module:
                    mod_lbl = QLabel(t.module)
                    mod_lbl.setStyleSheet("color: #007AFF; font-size: 11px; font-weight: 600; background: #E5F1FF; padding: 3px 8px; border-radius: 6px; border: none;")
                    desc_h_layout.addWidget(mod_lbl)

                pri_color = "#FF3B30" if t.priority == "高" else ("#FF9500" if t.priority == "中" else "#34C759")
                pri_bg = "#FFEBEA" if t.priority == "高" else ("#FFF4E5" if t.priority == "中" else "#EAF9ED")
                pri_lbl = QLabel(t.priority)
                pri_lbl.setStyleSheet(f"color: {pri_color}; font-size: 11px; font-weight: 600; background: {pri_bg}; padding: 3px 8px; border-radius: 6px; border: none;")
                desc_h_layout.addWidget(pri_lbl)

                desc_h_layout.addStretch()
                clayout.addLayout(desc_h_layout)

                # Bottom info (date/time)
                btm_layout = QHBoxLayout()
                date_lbl = QLabel(f"🕐 {t.plan_end}" if t.plan_end else "未定")
                date_lbl.setStyleSheet("color: #8E8E93; font-size: 11px; border: none;")
                btm_layout.addWidget(date_lbl)
                btm_layout.addStretch()
                clayout.addLayout(btm_layout)

                col_v_layout.addWidget(card)

            self.kanban_layout.addWidget(col_widget)


    @staticmethod
    def calculate_days(start_str, end_str, today=None):
        if not start_str or not end_str:
            return "", ""
        try:
            if today is None:
                today = date.today()
            start = datetime.strptime(start_str, "%Y-%m-%d").date()
            end = datetime.strptime(end_str, "%Y-%m-%d").date()
            spent = max((today - start).days, 0)
            left = (end - today).days
            return spent, left
        except Exception:
            return "", ""

    @staticmethod
    def calculate_progress(spent, left):
        if not isinstance(spent, int) or spent < 0:
            return None
        if isinstance(left, int) and left >= 0 and (spent + left) > 0:
            return spent * 100.0 / (spent + left)
        if isinstance(left, int) and left < 0:
            return 100.0
        return None

    # ============ 按钮逻辑 ============

    def _get_selected_task(self) -> Optional[Task]:
        row = self.table.currentRow()
        if row < 0 or row >= len(self.tasks):
            return None
        return self.tasks[row]

    def new_task(self):
        dlg = TaskDialog(self, task=None)
        if dlg.exec() == QDialog.Accepted:
            from db.task_repository import create_task
            task = dlg.get_task()
            create_task(task)
            self.load_tasks()

    def edit_task(self):
        current = self._get_selected_task()
        if not current:
            QMessageBox.information(self, "提示", "请先在列表中选中要编辑的任务。")
            return

        # 记录旧状态
        old_status = current.status

        dlg = TaskDialog(self, task=current)
        if dlg.exec() == QDialog.Accepted:
            from db.task_repository import update_task
            new_task = dlg.get_task()
            new_task.id = current.id
            update_task(new_task)

            # 检查 XP 奖励条件：状态变为 "已上线（归档）" 且旧状态不是
            if new_task.status == "已上线（归档）" and old_status != "已上线（归档）":
                self.award_xp(new_task.priority)

            self.load_tasks()

    def award_xp(self, priority: str):
        """根据优先级计算并增加 XP，带动画"""
        amount = XP_MAP.get(priority, 20)

        # 数据库增加
        add_xp(amount)

        # 播放动画更新 UI
        self.animate_xp_change(amount)

    def refresh_xp_display(self):
        """读取数据库刷新 XP 显示"""
        total_xp = get_xp()
        level = get_level(total_xp)
        current_level_xp = total_xp % 1000

        self.level_label.setText(f"Lv.{level}")
        self.xp_bar.setValue(current_level_xp)
        self.xp_text.setText(f"{current_level_xp} / 1000 XP")

    def animate_xp_change(self, amount: int):
        """XP 增加动画"""
        start_val = self.xp_bar.value()
        end_val = start_val + amount

        # 如果升级了，动画分两段播或者直接跳过（简单处理：如果超过1000，则只能演示到1000后归零再走）
        # 这里做一个简单的动画，如果当前 XP + increment > 1000，说明升级

        current_total = get_xp() # 这已经是增加后的总值了
        level = get_level(current_total)
        current_xp_in_level = current_total % 1000

        # 简单处理：更新等级文字，进度条从 start_val 用动画跑到 current_xp_in_level
        # 注意：如果升级了，进度条应该是从 start_val -> 1000 (然后重置为0) -> current_xp_in_level
        # 这里为了简化代码，直接调用 refresh_xp_display 更新文字，只给进度条做个简单动画

        self.level_label.setText(f"Lv.{level}")
        self.xp_text.setText(f"{current_xp_in_level} / 1000 XP")

        # 使用 QPropertyAnimation
        self.anim = QPropertyAnimation(self.xp_bar, b"value")
        self.anim.setDuration(800)
        self.anim.setStartValue(start_val)

        # 判断是否跨级
        if start_val + amount >= 1000:
            # 跨级情况：先填满
            self.anim.setEndValue(1000)
            self.anim.finished.connect(lambda: self._animate_next_level(current_xp_in_level))
        else:
            self.anim.setEndValue(current_xp_in_level)

        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

    def _animate_next_level(self, target_value):
        """第二阶段动画（升级后）"""
        self.xp_bar.setValue(0)
        self.anim2 = QPropertyAnimation(self.xp_bar, b"value")
        self.anim2.setDuration(500)
        self.anim2.setStartValue(0)
        self.anim2.setEndValue(target_value)
        self.anim2.setEasingCurve(QEasingCurve.OutCubic)
        self.anim2.start()

    def delete_task(self):
        current = self._get_selected_task()
        if not current:
            QMessageBox.information(self, "提示", "请先在列表中选中要删除的任务。")
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除【{current.title}】吗？此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        from db.task_repository import delete_task
        delete_task(current.id)
        self.load_tasks()

    def open_archive(self):
        """打开归档页面"""
        dlg = ArchiveDialog(self)
        dlg.exec()
        # 归档变化后，主界面数量有变化，刷新一下
        self.load_tasks()

    def open_calendar(self):
        """打开日历视图"""
        dlg = CalendarDialog(self)
        dlg.exec()

    def open_dashboard(self):
        """打开仪表盘"""
        dlg = DashboardDialog(self)
        dlg.exec()

    def export_to_csv(self):
        """导出任务到 CSV文件"""
        import csv
        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出 CSV", "", "CSV Files (*.csv);;All Files (*)"
        )
        if not file_path:
            return

        try:
            with open(file_path, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["标题", "模块", "版本", "状态", "优先级", "开始日期", "截止日期", "备注"])

                from db.task_repository import list_tasks
                all_tasks = list_tasks()
                for task in all_tasks:
                    writer.writerow([
                        task.title,
                        task.module,
                        task.version,
                        task.status,
                        task.priority,
                        task.plan_start,
                        task.plan_end,
                        task.notes
                    ])
            QMessageBox.information(self, "成功", f"成功导出到 {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {e}")

    def refresh_maxim(self, event):
        """随机刷新语录"""
        maxim = get_random_maxim()
        self.maxim_label.setText(f"💡 灵感：{maxim}")

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_QSS)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
