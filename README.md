# 记账本 · BillAccount

> 轻量级个人记账桌面应用 | Lightweight personal finance desktop app

[中文](#中文) | [English](#english)

---

## 中文

### 简介

记账本是一款基于 Python 的本地个人财务管理工具。使用 SQLite 存储数据，界面基于 CustomTkinter 构建，支持暗色/亮色主题一键切换，提供日/周/月/年多维度统计分析，数据可导入导出，并支持打包为独立 .exe 文件跨机器运行。

### 功能

- **记账核心**：收入/支出记录，支持分类、日期、备注，可编辑和删除
- **14 种默认分类**：工资、奖金、理财、兼职 / 餐饮、交通、购物、住房、娱乐、医疗、教育、通讯 等
- **本地存储**：SQLite 数据库，数据完全由你掌控
- **可配置路径**：自定义数据库文件存储位置，迁移数据一键完成
- **暗色/亮色主题**：一键切换，即时生效，配置持久化
- **多维度统计**：日/周/月/年 四种周期，饼图 + 柱状图可视化，鼠标悬停查看详情
- **数据导入导出**：CSV（兼容 Excel）和 JSON（完整备份）两种格式
- **GUI 打包安装**：运行 `build.py` 弹出可视化安装界面，选择路径一键打包为 .exe

### 安装与运行

```bash
# 1. 克隆仓库
git clone https://github.com/majiabinaaa/BillAccount-Local.git
cd BillAccount-Local

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行
python main.py
```

### 打包为 .exe

```bash
python build.py
```

弹出 GUI 界面，选择安装目录，点击"开始打包安装"即可生成 `BillAccount.exe`。

### 项目结构

```
BillAccount/
├── main.py                     # 入口
├── build.py                    # GUI 打包安装工具
├── requirements.txt            # 依赖清单
├── core/
│   ├── database.py             # SQLite CRUD + 统计查询
│   ├── models.py               # Bill / Category 数据类
│   └── config_manager.py       # 配置读写（主题、路径）
├── ui/
│   ├── app.py                  # CTk 主应用
│   ├── main_window.py          # 主布局（侧边栏 + 页面）
│   ├── sidebar.py              # 导航栏
│   ├── pages/
│   │   ├── dashboard.py        # 仪表盘（今日/本月概览）
│   │   ├── add_bill.py         # 记一笔
│   │   ├── bill_list.py        # 账单列表（筛选/搜索/分页）
│   │   ├── summary.py          # 统计分析（图表）
│   │   └── settings.py         # 设置（主题/路径/导入导出）
│   └── components/
│       ├── bill_form.py        # 账单表单组件
│       └── chart_view.py       # matplotlib 图表组件
└── utils/
    ├── date_utils.py           # 日期工具
    └── export_import.py        # 文件对话框导入导出
```

### 技术栈

| 层 | 技术 |
|---|---|
| UI | CustomTkinter |
| 图表 | matplotlib |
| 数据库 | SQLite (sqlite3) |
| 打包 | PyInstaller |
| 配置 | JSON |

### 许可

MIT License

### 更新历史

| 版本 | 日期 | 说明 |
|------|------|------|
| V2.3 | 2026-05-28 | 修复所有弹窗黑屏问题，修复操作栏按钮透明，优化编辑对话框 |
| V2.2 | 2026-05-27 | 修复按钮/下拉框透明问题，新增 StyledComboBox 组件 |
| V2.1 | 2026-05-27 | 新增背景选择功能（12角色36图），新增消费画像页面 |

---

## English

### Overview

BillAccount is a Python-based personal finance management tool. Data is stored locally in SQLite, the UI is built with CustomTkinter, featuring one-click dark/light theme switching, multi-period statistics (daily/weekly/monthly/yearly), data import/export, and standalone .exe packaging for cross-machine deployment.

### Features

- **Core Bookkeeping**: Record income/expense with categories, dates, notes; edit and delete entries
- **14 Default Categories**: Salary, bonus, investments, side jobs / dining, transport, shopping, housing, entertainment, medical, education, telecom, etc.
- **Local Storage**: SQLite database — your data stays with you
- **Configurable Path**: Customize database file location with one-click data migration
- **Dark / Light Theme**: Instant toggle, preference persisted across sessions
- **Multi-Period Statistics**: Day / Week / Month / Year views with pie + bar charts. Hover over chart elements for details
- **Import / Export**: CSV (Excel-compatible) and JSON (full backup) formats
- **GUI Packager**: Run `build.py` for a visual installer — select install path and build a standalone .exe

### Install & Run

```bash
# 1. Clone
git clone https://github.com/majiabinaaa/BillAccount-Local.git
cd BillAccount-Local

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch
python main.py
```

### Build .exe

```bash
python build.py
```

A GUI window opens — choose an install directory, click the build button, and `BillAccount.exe` is generated.

### Project Structure

```
BillAccount/
├── main.py                     # Entry point
├── build.py                    # GUI build & installer tool
├── requirements.txt            # Dependencies
├── core/
│   ├── database.py             # SQLite CRUD + summary queries
│   ├── models.py               # Bill / Category dataclasses
│   └── config_manager.py       # Config I/O (theme, path)
├── ui/
│   ├── app.py                  # CTk main application
│   ├── main_window.py          # Layout (sidebar + content area)
│   ├── sidebar.py              # Navigation sidebar
│   ├── pages/
│   │   ├── dashboard.py        # Dashboard (today/month overview)
│   │   ├── add_bill.py         # Add bill form
│   │   ├── bill_list.py        # Bill list (filters/search/pagination)
│   │   ├── summary.py          # Statistics & charts
│   │   └── settings.py         # Settings (theme/path/import-export)
│   └── components/
│       ├── bill_form.py        # Reusable bill form
│       └── chart_view.py       # matplotlib chart component
└── utils/
    ├── date_utils.py           # Date helpers
    └── export_import.py        # File dialog import/export
```

### Tech Stack

| Layer | Technology |
|---|---|
| UI | CustomTkinter |
| Charts | matplotlib |
| Database | SQLite (sqlite3) |
| Packaging | PyInstaller |
| Config | JSON |

### License

MIT License

### Changelog

| Version | Date | Description |
|---------|------|-------------|
| V2.3 | 2026-05-28 | Fix dialog black screen, fix transparent action buttons, improve edit dialog |
| V2.2 | 2026-05-27 | Fix button/combobox transparency, add StyledComboBox component |
| V2.1 | 2026-05-27 | Add background selection (12 characters, 36 images), add consumer profile page |
