# life-manager-skill

生活事务管家 Skill：待办管理、记账统计、定时提醒一体化。

## 触发条件

当用户需要处理以下日常事务时调用本 Skill：
- 添加/查看/完成/删除待办事项
- 记录收支、查看分类统计和月度小结
- 设置定时提醒（自然语言时间描述）

## 使用方式

本 Skill 通过 CLI 入口 `skill.py` 提供服务，各子功能通过子命令路由：

```bash
# 待办管理
python skill.py todo add "提交简历" --due "明天 18:00" --priority high
python skill.py todo list [--status pending|done] [--date 今天]
python skill.py todo done <id>
python skill.py todo delete <id>
python skill.py todo stats

# 记账统计
python skill.py ledger add 咖啡 -15 --category 餐饮
python skill.py ledger add 工资 +8000 --category 收入
python skill.py ledger list [--category 餐饮] [--month 2026-09]
python skill.py ledger stats [--month 2026-09]

# 定时提醒
python skill.py remind "明天上午9点 开会"
python skill.py remind list
python skill.py remind delete <id>
```

## 数据存储

所有数据统一存储在本地 SQLite 数据库（`data/life.db`），首次运行时自动创建。

## 子功能说明

### 1. 待办管理 (todo)
- 添加待办，支持截止日期和优先级（high/medium/low）
- 按状态/日期筛选查看
- 标记完成、删除
- 统计概览（总数、已完成、待办、逾期）

### 2. 记账统计 (ledger)
- 记录收入和支出（金额用 +/- 区分，或 --type 指定）
- 分类管理（餐饮、交通、购物、居住、娱乐、收入等）
- 按月/分类筛选和统计
- 月度小结（总收入、总支出、结余、分类占比）

### 3. 定时提醒 (reminder)
- 自然语言时间解析（"明天上午9点"、"每周五下午"、"3小时后"）
- 支持一次性提醒和周期提醒（cron 表达式）
- 查看/删除已有提醒

## 设计要点

- 完全离线运行，无需 API Key
- 单入口多子命令路由，便于 Agent 调用
- SQLite 统一持久化，数据可迁移
- 自然语言时间解析器，支持中英文混合描述
