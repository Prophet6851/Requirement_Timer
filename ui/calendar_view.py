from datetime import datetime, date
from typing import List

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QCalendarWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor

from models.task import Task

# 跟主窗口保持一致的“已完成状态”定义
COMPLETED_STATUSES = ["验收完", "测试回归bug", "已上线（归档）"]


class CalendarDialog(QDialog):
    """日历视图：按日期查看任务排期"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("日历视图 - 需求排期")
        self.resize(920, 600)

        self.all_tasks: List[Task] = []
        self._build_ui()
        self.load_tasks()

    # ===== UI 搭建 =====

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
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # 上：日历 + 概要区域
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.setFirstDayOfWeek(Qt.Monday)
        self.calendar.setMinimumDate(QDate(2000, 1, 1))
        self.calendar.setMaximumDate(QDate(2100, 12, 31))
        self.calendar.setFixedWidth(360)
        top_layout.addWidget(self.calendar)

        right_box = QVBoxLayout()
        right_box.setSpacing(6)

        self.date_label = QLabel("")
        self.date_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #111111;")
        right_box.addWidget(self.date_label)

        self.count_label = QLabel("当天任务：0")
        self.count_label.setStyleSheet("color: #6B7280; font-size: 11px;")
        right_box.addWidget(self.count_label)

        right_box.addStretch()

        close_btn = QPushButton("关闭")
        close_btn.setFixedWidth(80)
        right_box.addWidget(close_btn, alignment=Qt.AlignRight)

        top_layout.addLayout(right_box)
        layout.addLayout(top_layout)

        # 下：当日任务列表
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "标题", "模块", "状态", "优先级",
            "开始日期", "截止日期", "备注",
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(24)

        layout.addWidget(self.table)

        # 信号
        self.calendar.selectionChanged.connect(self.on_date_changed)
        close_btn.clicked.connect(self.accept)

    # ===== 数据处理 =====

    @staticmethod
    def _parse_date(s: str):
        if not s:
            return None
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None

    def load_tasks(self):
        """从数据库加载全部任务"""
        from db.task_repository import list_tasks

        self.all_tasks = list_tasks()
        # 默认用当前选中的日期刷新一次
        self.update_for_date(self.calendar.selectedDate())

    def on_date_changed(self):
        qd = self.calendar.selectedDate()
        self.update_for_date(qd)

    def update_for_date(self, qdate: QDate):
        """根据选中的日期刷新下方任务列表"""
        day = date(qdate.year(), qdate.month(), qdate.day())

        self.date_label.setText(f"{day.strftime('%Y-%m-%d')} 的任务排期")

        tasks_for_day: List[Task] = []
        for t in self.all_tasks:
            start = self._parse_date(t.plan_start)
            end = self._parse_date(t.plan_end)

            # 规则：选中日期 ∈ [start, end] 就视为当天在进行这个任务
            if start and end:
                if start <= day <= end:
                    tasks_for_day.append(t)
            elif start:
                if day == start:
                    tasks_for_day.append(t)
            elif end:
                if day == end:
                    tasks_for_day.append(t)
            else:
                # 没有日期信息的任务，日历视图里忽略
                continue

        self.count_label.setText(f"当天任务：{len(tasks_for_day)}")

        # 填充表格
        self.table.setRowCount(len(tasks_for_day))
        for row, t in enumerate(tasks_for_day):
            values = [
                t.title,
                t.module,
                t.status,
                t.priority,
                t.plan_start or "",
                t.plan_end or "",
                t.notes or "",
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(val or "")
                # 已完成状态：整行文字用淡绿色
                if t.status in COMPLETED_STATUSES:
                    item.setForeground(QColor("#34C759"))
                self.table.setItem(row, col, item)

        self.table.resizeColumnsToContents()
