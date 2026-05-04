import matplotlib
matplotlib.use('QtAgg')

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

from datetime import datetime, date
from db.task_repository import list_tasks

class DashboardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("数据统计仪表盘")
        self.resize(800, 500)
        self.tasks = list_tasks()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Matplotlib Figures
        self.fig, (self.ax_burndown, self.ax_radar) = plt.subplots(1, 2, figsize=(10, 5))
        self.fig.patch.set_facecolor('#F5F5F7')
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        self._plot_burndown()
        self._plot_radar()

    def _plot_burndown(self):
        # 简单燃尽图：基于截止日期统计待完成任务数
        # 实际更严谨的话需要按历史节点，由于目前只有当前快照，我们按截止日期画
        self.ax_burndown.clear()
        self.ax_burndown.set_title("燃尽图 (按截止日期统计待完成)")

        # 筛选出没有完成的任务
        active_tasks = [t for t in self.tasks if t.status not in ["验收完", "测试回归bug", "已上线（归档）"] and t.plan_end]
        if not active_tasks:
            self.ax_burndown.text(0.5, 0.5, "没有待完成任务", ha='center')
            return

        # 按截止日期排序
        active_tasks.sort(key=lambda x: x.plan_end)

        dates = []
        counts = []
        current_count = len(active_tasks)

        # 统计每一天结束后的剩余任务数
        from collections import defaultdict
        end_date_counts = defaultdict(int)
        for t in active_tasks:
            end_date_counts[t.plan_end] += 1

        sorted_dates = sorted(end_date_counts.keys())

        for d in sorted_dates:
            dates.append(d[5:]) # MM-DD
            counts.append(current_count)
            current_count -= end_date_counts[d]

        if sorted_dates:
            dates.append("之后")
            counts.append(0)

        self.ax_burndown.plot(dates, counts, marker='o', linestyle='-', color='#007AFF')
        self.ax_burndown.set_ylabel("剩余任务数")
        self.ax_burndown.tick_params(axis='x', rotation=45)

    def _plot_radar(self):
        self.ax_radar.clear()
        self.ax_radar.remove()
        self.ax_radar = self.fig.add_subplot(1, 2, 2, polar=True)
        self.ax_radar.set_title("模块精力分布雷达图")

        from collections import defaultdict
        module_counts = defaultdict(int)
        for t in self.tasks:
            mod = t.module or "未分类"
            module_counts[mod] += 1

        if not module_counts:
            return

        categories = list(module_counts.keys())
        values = list(module_counts.values())

        # 闭合多边形
        values += values[:1]
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]

        self.ax_radar.plot(angles, values, color='#34C759', linewidth=2)
        self.ax_radar.fill(angles, values, color='#34C759', alpha=0.25)

        self.ax_radar.set_xticks(angles[:-1])
        # 使用 SimHei 显示中文
        self.ax_radar.set_xticklabels(categories)
        self.ax_radar.set_yticks([])

