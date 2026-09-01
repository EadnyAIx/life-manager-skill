# 生活事务管家 Skill

> 待办管理、记账统计、定时提醒一体化，本地 SQLite 持久化，完全离线可用。

## ✨ 功能特性

### 📋 待办管理
- 添加待办：支持截止日期、优先级（high/medium/low）
- 查看待办：按状态/日期筛选
- 标记完成、删除
- 统计概览（总数/待办/已完成/逾期）

### 💰 记账统计
- 记录收入/支出，自动分类
- 分类管理（餐饮、交通、购物、居住、娱乐、收入等）
- 按月/分类筛选和统计
- 月度小结（收入/支出/结余/分类占比）

### ⏰ 定时提醒
- 自然语言时间解析："明天上午9点"、"每周五下午"、"3小时后"
- 一次性提醒 + 周期提醒（cron）
- 查看/删除提醒

## 🏗️ 架构

```
skill.py (CLI 入口，路由分发)
 ├── todo.py       待办管理
 ├── ledger.py     记账统计
 ├── reminder.py   定时提醒
 ├── time_parser.py  自然语言时间解析
 └── storage.py    SQLite 统一存储
```

## 📦 安装

```bash
git clone <repo-url>
cd life-manager-skill
pip install -r requirements.txt
```

## 🚀 使用方法

### 待办管理

```bash
# 添加（相对时间 + 优先级）
python skill.py todo add "提交简历" --due "明天 18:00" --priority high
python skill.py todo add "购买礼物" --due "周六"

# 查看
python skill.py todo list
python skill.py todo list --status pending
python skill.py todo list --date 今天

# 操作
python skill.py todo done 1
python skill.py todo delete 2
python skill.py todo stats
```

### 记账

```bash
# 记录（+ 收入 / - 支出，也可用 --type）
python skill.py ledger add 咖啡 -15 --category 餐饮
python skill.py ledger add 工资 8000 --type income --category 收入

# 查看
python skill.py ledger list
python skill.py ledger list --category 餐饮
python skill.py ledger list --month 2026-09

# 统计
python skill.py ledger stats
python skill.py ledger stats --month 2026-09
```

### 定时提醒

```bash
python skill.py remind "明天上午9点 项目周会"
python skill.py remind "每周五下午 写周报"
python skill.py remind "3小时后 喝水休息"
python skill.py remind list
python skill.py remind delete 1
```

## 🧪 测试

```bash
python -m pytest tests/ -v
```

## 📁 项目结构

```
life-manager-skill/
├── SKILL.md              # Skill 能力说明
├── skill.py              # CLI 入口
├── todo.py               # 待办管理
├── ledger.py             # 记账统计
├── reminder.py           # 定时提醒
├── time_parser.py        # 自然语言时间解析
├── storage.py            # SQLite 存储
├── requirements.txt
├── .gitignore
└── tests/
    ├── test_time_parser.py
    ├── test_todo.py
    ├── test_ledger.py
    └── test_reminder.py
```

## 📄 License

MIT
