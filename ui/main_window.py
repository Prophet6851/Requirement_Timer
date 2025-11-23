from datetime import datetime, date
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QSizePolicy, QMessageBox, QDialog, QFormLayout,
    QLineEdit, QComboBox, QDateEdit, QTextEdit,
    QDialogButtonBox, QStyledItemDelegate
)
from PySide6.QtCore import Qt, QDate, QRect
from PySide6.QtGui import QColor, QPainter

from models.task import Task
from .calendar_view import CalendarDialog  # 新增：引入日历视图对话框

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
        self.setMinimumWidth(480)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 12)
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

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("备注：依赖项、沟通记录、注意事项等……")
        self.notes_edit.setFixedHeight(120)
        form.addRow("备注：", self.notes_edit)

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
        self.setStyleSheet("""
            QDialog {
                background: #F5F5F7;
            }
            QTableWidget {
                background: #FFFFFF;
                border: 1px solid #E5E5EA;
                gridline-color: #E5E5EA;
                alternate-background-color: #F9F9FB;
            }
            QHeaderView::section {
                background: #F2F2F7;
                padding: 6px;
                border: none;
                font-weight: 500;
                color: #1C1C1E;
            }
            QPushButton {
                border-radius: 6px;
                padding: 6px 16px;
                border: 1px solid #D1D1D6;
                background: #FFFFFF;
                color: #1C1C1E;
            }
            QPushButton:hover {
                background: #F2F2F7;
            }
            QPushButton#dangerButton {
                background: #FF3B30;
                color: white;
                border: 1px solid #CC2D25;
            }
            QPushButton#dangerButton:hover {
                background: #D8342F;
            }
            QPushButton#primaryButton {
                background: #007AFF;
                color: white;
                border: 1px solid #0060DF;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

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
        self.resize(1100, 650)

        self.tasks: list[Task] = []

        self._build_ui()
        self.load_tasks()

    # ============ UI ============

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        self.setStyleSheet("""
            QMainWindow {
                background: #F5F5F7;
            }
            QTableWidget {
                background: #FFFFFF;
                border: 1px solid #E5E5EA;
                gridline-color: #E5E5EA;
                alternate-background-color: #F9F9FB;
            }
            QHeaderView::section {
                background: #F2F2F7;
                padding: 6px;
                border: none;
                font-weight: 500;
                color: #1C1C1E;
            }
            QLineEdit, QComboBox, QDateEdit, QTextEdit {
                background: #FFFFFF;
                border: 1px solid #D1D1D6;
                border-radius: 6px;
                padding: 4px 8px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
                border: 1px solid #007AFF;
                box-shadow: 0 0 0 1px rgba(0,122,255,0.15);
            }
            QPushButton {
                border-radius: 6px;
                padding: 6px 16px;
                border: 1px solid #D1D1D6;
                background: #FFFFFF;
                color: #1C1C1E;
            }
            QPushButton:hover {
                background: #F2F2F7;
            }
            QPushButton#primaryButton {
                background: #007AFF;
                color: #FFFFFF;
                border: 1px solid #0060DF;
            }
            QPushButton#primaryButton:hover {
                background: #0059D6;
            }
        """)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)

        # 顶部条：标题 + 统计 + 筛选
        header_layout = QHBoxLayout()
        header_layout.setSpacing(6)

        title_label = QLabel("Requirement Timer")
        title_label.setStyleSheet("font-size: 15px; font-weight: 600; color: #111111;")
        header_layout.addWidget(title_label)

        self.summary_label = QLabel("当前任务：0 / 归档：0")
        self.summary_label.setStyleSheet("color: #6B7280; font-size: 11px;")
        header_layout.addWidget(self.summary_label)

        header_layout.addStretch()

        status_label = QLabel("状态：")
        status_label.setStyleSheet("font-size: 11px;")
        self.status_filter = QComboBox()
        self.status_filter.addItem("全部")
        # 过滤器这里不包含“已上线（归档）”，因为那是归档页面
        for s in STATUS_OPTIONS:
            if s != "已上线（归档）":
                self.status_filter.addItem(s)
        self.status_filter.setFixedWidth(130)

        priority_label = QLabel("优先级：")
        priority_label.setStyleSheet("font-size: 11px;")
        self.priority_filter = QComboBox()
        self.priority_filter.addItem("全部")
        self.priority_filter.addItems(PRIORITY_OPTIONS)
        self.priority_filter.setFixedWidth(100)

        header_layout.addWidget(status_label)
        header_layout.addWidget(self.status_filter)
        header_layout.addWidget(priority_label)
        header_layout.addWidget(self.priority_filter)

        main_layout.addLayout(header_layout)

        # 中部：当前任务表格（不含已上线）
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
        self.table.setSortingEnabled(False)
        self.table.verticalHeader().setDefaultSectionSize(26)
        self.table.setItemDelegateForColumn(10, ProgressDelegate(self.table))

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)

        main_layout.addWidget(self.table)

        # 底部：操作按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(8)

        self.new_btn = QPushButton("新建")
        self.edit_btn = QPushButton("编辑")
        self.delete_btn = QPushButton("删除")
        self.refresh_btn = QPushButton("刷新")
        self.archive_btn = QPushButton("查看归档")
        self.calendar_btn = QPushButton("日历视图")   # 新增按钮
        self.export_btn = QPushButton("导出 CSV（后续）")
        self.about_btn = QPushButton("关于本软件")

        self.new_btn.setObjectName("primaryButton")

        bottom_layout.addWidget(self.new_btn)
        bottom_layout.addWidget(self.edit_btn)
        bottom_layout.addWidget(self.delete_btn)
        bottom_layout.addWidget(self.refresh_btn)
        bottom_layout.addWidget(self.archive_btn)
        bottom_layout.addWidget(self.calendar_btn)
        bottom_layout.addWidget(self.about_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.export_btn)

        main_layout.addLayout(bottom_layout)

        # 信号
        self.new_btn.clicked.connect(self.new_task)
        self.edit_btn.clicked.connect(self.edit_task)
        self.delete_btn.clicked.connect(self.delete_task)
        self.refresh_btn.clicked.connect(self.load_tasks)
        self.archive_btn.clicked.connect(self.open_archive)
        self.calendar_btn.clicked.connect(self.open_calendar)  # 新增：打开日历视图
        self.status_filter.currentIndexChanged.connect(self.load_tasks)
        self.priority_filter.currentIndexChanged.connect(self.load_tasks)
        self.about_btn.clicked.connect(self.show_about)

    # ============ 数据加载 ============

    def load_tasks(self):
        """当前页面：只显示 非 已上线（归档） 的任务；逾期/已完成显示规则更新"""
        from db.task_repository import list_tasks

        all_tasks = list_tasks()
        active_tasks = [t for t in all_tasks if t.status != "已上线（归档）"]
        archived_tasks = [t for t in all_tasks if t.status == "已上线（归档）"]

        status_f = self.status_filter.currentText()
        priority_f = self.priority_filter.currentText()

        def match(task: Task) -> bool:
            if status_f != "全部" and task.status != status_f:
                return False
            if priority_f != "全部" and task.priority != priority_f:
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

        dlg = TaskDialog(self, task=current)
        if dlg.exec() == QDialog.Accepted:
            from db.task_repository import update_task
            new_task = dlg.get_task()
            new_task.id = current.id
            update_task(new_task)
            self.load_tasks()

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
