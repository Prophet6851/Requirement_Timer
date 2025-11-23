# 📘 **Requirement Timer — 项目文档（v1.0）**

## 📝 1. 项目简介

**Requirement Timer** 是一个用于游戏策划（或任何需求管理角色）使用的 **本地桌面应用**，核心用于：

- 管理需求进度
- 查看任务推进天数
- 显示剩余天数（含逾期标红）
- 按状态/优先级筛选
- 使用进度条展示任务完成度
- 归档已上线内容
- 提供干净、现代的 Apple 风格 UI

整个项目使用 **Python + PySide6 + SQLite** 开发，可单机使用，也未来可封装为 exe。

------

## ⭐ 2. 核心功能概述（v1.0）

### ✅ **任务管理**

- 新建任务
- 编辑任务
- 删除任务
- 自动计算推进天数
- 自动计算剩余天数
- 按优先级/状态筛选
- 状态变更自动影响进度显示
- 逾期显示“已逾期”（红色）
- 完成状态显示“已完成”（绿色）

### 🎨 **现代 UI**

- Apple 风格 QSS
- 扁平圆角表格
- 蓝色 iOS 风格进度条
- 状态颜色区分
- 弹窗编辑更节省空间

### 📦 **归档系统**

- 已上线需求自动从主列表移除
- 专属“归档页面”存放历史任务
- 进度自动 100%
- 剩余天数显示“已完成”（绿色）

------

## 🗂️ 3. 状态逻辑说明

### **所有状态：**

```
策划中
交互案
美术
开发中
待验收
验收完
测试回归bug
已上线（归档）
```

### **属于“已完成”的状态：**

```
验收完
测试回归bug
已上线（归档）
```

### **显示逻辑：**

| 状态                | 剩余天数显示   | 进度条       |
| ------------------- | -------------- | ------------ |
| 非完成状态 & 未过期 | 正常显示       | 依推进计算   |
| 非完成状态 & 已过期 | 红色「已逾期」 | 保持自动计算 |
| 完成状态（任意）    | 绿色「已完成」 | 强制100%     |

------

## 🏗️ 4. 项目结构

```
RequirementTimer/
│
├── main.py                     # 程序入口
│
├── ui/
│   ├── __init__.py
│   └── main_window.py          # UI 主界面 + 弹窗编辑 + 归档界面
│
├── models/
│   ├── __init__.py
│   └── task.py                 # Task 数据结构（Model）
│
├── db/
│   ├── __init__.py
│   ├── database.py             # 初始化 SQLite
│   └── task_repository.py      # CRUD 操作
│
├── data/
│   └── task.db                 # SQLite 数据库文件
│
└── README.md（可选）
```

------

## 📦 5. 文件说明

### `main.py`

- 程序入口
- 创建 QApplication
- 加载 MainWindow

### `ui/main_window.py`

UI 总控，包括：

- 主界面
- 表格
- 筛选
- QSS（Apple 风格）
- TaskDialog（新增/编辑）
- ArchiveDialog（归档界面）
- ProgressDelegate（进度条绘制）

### `models/task.py`

- Task 数据结构
- 提供字段定义和类型支持

### `db/database.py`

- 初始化 SQLite 数据库
- 自动建库/建表

### `db/task_repository.py`

- task 的 CRUD 操作
- 包含：
  - create_task
  - update_task
  - delete_task
  - list_tasks（按创建时间排序）

------

## 🧪 6. 数据库结构（SQLite）

表名：`task`

字段：

| 字段       | 类型                | 说明                      |
| ---------- | ------------------- | ------------------------- |
| id         | INTEGER PRIMARY KEY | 自增 ID                   |
| title      | TEXT                | 标题                      |
| module     | TEXT                | 模块，例如 AI、系统、数据 |
| version    | TEXT                | 版本号                    |
| status     | TEXT                | 状态                      |
| priority   | TEXT                | 高/中/低                  |
| plan_start | TEXT                | 开始日期 YYYY-MM-DD       |
| plan_end   | TEXT                | 截止日期                  |
| notes      | TEXT                | 备注                      |

------

## 🎨 7. UI 设计风格（Apple风）

- 背景浅灰：#F5F5F7
- 卡片白底：#FFFFFF
- 蓝色主色：#007AFF
- 灰色边框：#E5E5EA
- 表头：浅灰 #F2F2F7
- 输入框圆角：6px
- 按钮圆角：6px
- 进度条圆角：高度一半
- Apple 绿：#34C759
- Apple 红：#FF3B30

------

## ⚙️ 8. 如何运行（开发环境）

### 创建虚拟环境

```
python -m venv .venv
```

### 激活

```
.venv\Scripts\activate
```

### 安装依赖

```
pip install PySide6
```

### 启动

```
python main.py
```

------

## 📦 9. 如何打包为 EXE（可选）

使用 PyInstaller：

```
pyinstaller --noconfirm --windowed --clean ^
  --add-data "data;data" ^
  --icon=icon.ico ^
  main.py
```

生成的 exe 在 `dist/main/` 下。

我可以帮你生成专属的 `.spec` 文件和图标资源。

------

## 🚀 10. 后续可扩展（v2.0 想法）

- 日历视图（查看时间线）
- 甘特图（任务时间视图）
- 自动生成周报（Markdown/Word）
- Excel 导出
- 多用户同步（本地 → Web → 手机）
- 自动通知（到期提醒）
- 状态自动流转
- 左侧“模块列表”树展示
- 深色模式

你想做哪个我可以继续帮你扩展。