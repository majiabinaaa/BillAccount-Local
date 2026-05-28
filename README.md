# 记账本 · BillAccount

> 轻量级个人记账桌面应用 | Lightweight personal finance desktop app

[中文](#中文) | [English](#english)

---

## 中文

### 简介

记账本是一款基于 Python 的本地个人财务管理工具。使用 PySide6 (Qt) 构建 Apple 风格界面，SQLite 存储数据，提供日/周/月/年多维度统计分析、消费画像、精美报告导出，支持自定义背景主题，数据可导入导出，并支持打包为独立 .exe 文件跨机器运行。

### 功能

- **记账核心**：收入/支出记录，支持分类、日期、备注，可编辑和删除
- **14 种默认分类**：工资、奖金、理财、兼职 / 餐饮、交通、购物、住房、娱乐、医疗、教育、通讯 等
- **仪表盘**：今日/本月收支概览，快速导航
- **统计分析**：日/周/月/年四种周期，饼图 + 柱状图可视化
- **消费画像**：个性化消费者人格分析，财务健康评分，支出 Top 5 排行
- **导出报告**：生成精美的 PNG 报告（周报/月报/年报），手帐风格
- **自定义背景**：星穹铁道、绝区零、鸣潮、原神四大主题，12 位角色、36 张背景图
- **数据导入导出**：CSV（兼容 Excel）和 JSON（完整备份）两种格式
- **本地存储**：SQLite 数据库，数据完全由你掌控
- **可配置路径**：自定义数据库文件存储位置，迁移数据一键完成
- **GUI 打包安装**：运行 `build.py` 弹出可视化安装界面，选择路径一键打包为 .exe

### 截图

> 界面采用 Apple 风格设计，支持自定义角色背景

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
BillAccountV2.1/
├── main.py                     # 入口（支持 --export 命令行导出）
├── build.py                    # GUI 打包安装工具
├── requirements.txt            # 依赖清单
├── core/
│   ├── database.py             # SQLite CRUD + 统计查询
│   ├── models.py               # Bill / Category 数据类
│   ├── config_manager.py       # 配置读写
│   ├── analytics.py            # 消费画像 + 财务健康评分
│   ├── report_generator.py     # 报告数据生成
│   ├── report_renderer.py      # 报告 PNG 渲染
│   └── pdf_exporter.py         # PDF 导出
├── ui/
│   ├── app.py                  # PySide6 主应用
│   ├── main_window.py          # 主布局（侧边栏 + 页面）
│   ├── sidebar.py              # 导航栏
│   ├── theme.py                # Apple 风格设计系统 + QSS 样式表
│   ├── utils.py                # UI 工具函数
│   ├── dialogs.py              # 统一样式对话框
│   ├── custom_dialog.py        # 自定义对话框工具
│   ├── pages/
│   │   ├── dashboard.py        # 仪表盘（今日/本月概览）
│   │   ├── add_bill.py         # 记一笔
│   │   ├── bill_list.py        # 账单列表（筛选/搜索/分页）
│   │   ├── summary.py          # 统计分析（图表）
│   │   ├── profile.py          # 消费画像（人格 + 健康评分）
│   │   ├── export_page.py      # 导出报告（PNG 报告生成）
│   │   ├── bg_select.py        # 背景选择（角色主题）
│   │   └── settings.py         # 设置（路径/导入导出/清空数据）
│   └── components/
│       ├── bill_form.py        # 账单表单组件
│       ├── chart_view.py       # matplotlib 图表组件
│       ├── card.py             # 卡片容器
│       ├── stat_card.py        # 统计卡片
│       ├── badge.py            # 标签组件
│       ├── progress_bar.py     # 进度条
│       ├── section_title.py    # 区域标题
│       ├── empty_state.py      # 空状态占位
│       └── styled_combo.py     # 美化下拉框
└── utils/
    ├── date_utils.py           # 日期工具
    └── export_import.py        # 文件对话框导入导出
```

### 技术栈

| 层 | 技术 |
|---|---|
| UI | PySide6 (Qt6) |
| 样式 | QSS (Apple iOS 风格) |
| 图表 | matplotlib |
| 数据库 | SQLite (sqlite3) |
| 打包 | PyInstaller |
| 配置 | JSON |

### 更新历史

| 版本 | 日期 | 说明 |
|------|------|------|
| V2.3 | 2026-05-28 | 修复所有弹窗黑屏问题，修复操作栏按钮透明，优化编辑对话框 |
| V2.2 | 2026-05-27 | 修复按钮/下拉框透明问题，新增 StyledComboBox 组件 |
| V2.1 | 2026-05-27 | 新增背景选择功能（12角色36图），新增消费画像页面 |

### 许可

MIT License

---

## English

### Overview

BillAccount is a Python-based personal finance management tool with an Apple-style UI built using PySide6 (Qt). Data is stored locally in SQLite, featuring multi-period statistics, consumer profile analysis, beautiful PNG report export, custom background themes, data import/export, and standalone .exe packaging.

### Features

- **Core Bookkeeping**: Record income/expense with categories, dates, notes; edit and delete entries
- **14 Default Categories**: Salary, bonus, investments, side jobs / dining, transport, shopping, housing, entertainment, medical, education, telecom, etc.
- **Dashboard**: Today/month overview with quick navigation
- **Statistics**: Day / Week / Month / Year views with pie + bar charts
- **Consumer Profile**: Personalized personality analysis, financial health score, top 5 expense ranking
- **Report Export**: Generate beautiful PNG reports (weekly/monthly/yearly) in journal style
- **Custom Backgrounds**: 4 themes (Honkai: Star Rail, Zenless Zone Zero, Wuthering Waves, Genshin Impact), 12 characters, 36 background images
- **Import / Export**: CSV (Excel-compatible) and JSON (full backup) formats
- **Local Storage**: SQLite database — your data stays with you
- **Configurable Path**: Customize database file location with one-click data migration
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
BillAccountV2.1/
├── main.py                     # Entry point (supports --export CLI)
├── build.py                    # GUI build & installer tool
├── requirements.txt            # Dependencies
├── core/
│   ├── database.py             # SQLite CRUD + summary queries
│   ├── models.py               # Bill / Category dataclasses
│   ├── config_manager.py       # Config I/O
│   ├── analytics.py            # Consumer profile + health score
│   ├── report_generator.py     # Report data generation
│   ├── report_renderer.py      # Report PNG rendering
│   └── pdf_exporter.py         # PDF export
├── ui/
│   ├── app.py                  # PySide6 main application
│   ├── main_window.py          # Layout (sidebar + content area)
│   ├── sidebar.py              # Navigation sidebar
│   ├── theme.py                # Apple-style design system + QSS
│   ├── utils.py                # UI utility functions
│   ├── dialogs.py              # Unified styled dialogs
│   ├── custom_dialog.py        # Custom dialog utilities
│   ├── pages/
│   │   ├── dashboard.py        # Dashboard (today/month overview)
│   │   ├── add_bill.py         # Add bill form
│   │   ├── bill_list.py        # Bill list (filters/search/pagination)
│   │   ├── summary.py          # Statistics & charts
│   │   ├── profile.py          # Consumer profile (personality + health)
│   │   ├── export_page.py      # Export reports (PNG generation)
│   │   ├── bg_select.py        # Background selection (character themes)
│   │   └── settings.py         # Settings (path/import-export/clear data)
│   └── components/
│       ├── bill_form.py        # Reusable bill form
│       ├── chart_view.py       # matplotlib chart component
│       ├── card.py             # Card container
│       ├── stat_card.py        # Statistics card
│       ├── badge.py            # Badge component
│       ├── progress_bar.py     # Progress bar
│       ├── section_title.py    # Section title
│       ├── empty_state.py      # Empty state placeholder
│       └── styled_combo.py     # Styled combo box
└── utils/
    ├── date_utils.py           # Date helpers
    └── export_import.py        # File dialog import/export
```

### Tech Stack

| Layer | Technology |
|---|---|
| UI | PySide6 (Qt6) |
| Styles | QSS (Apple iOS style) |
| Charts | matplotlib |
| Database | SQLite (sqlite3) |
| Packaging | PyInstaller |
| Config | JSON |

### Changelog

| Version | Date | Description |
|---------|------|-------------|
| V2.3 | 2026-05-28 | Fix dialog black screen, fix transparent action buttons, improve edit dialog |
| V2.2 | 2026-05-27 | Fix button/combobox transparency, add StyledComboBox component |
| V2.1 | 2026-05-27 | Add background selection (12 characters, 36 images), add consumer profile page |

### License

MIT License
