"""生活事务管家 - CLI 入口。

用法:
    python skill.py todo add <内容> [--due 时间] [--priority high|medium|low]
    python skill.py todo list [--status pending|done] [--date YYYY-MM-DD]
    python skill.py todo done <id>
    python skill.py todo delete <id>
    python skill.py todo stats

    python skill.py ledger add <说明> <金额> [--category 分类] [--type income|expense]
    python skill.py ledger list [--category 分类] [--month YYYY-MM]
    python skill.py ledger stats [--month YYYY-MM]
    python skill.py ledger delete <id>

    python skill.py remind <自然语言描述>
    python skill.py remind list
    python skill.py remind delete <id>
    python skill.py remind toggle <id>
"""

import argparse
import sys

from storage import Storage
from todo import TodoManager
from ledger import LedgerManager
from reminder import ReminderManager


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skill", description="生活事务管家 Skill")
    subparsers = parser.add_subparsers(dest="module", required=True)

    # ----- todo -----
    todo = subparsers.add_parser("todo", help="待办管理")
    todo_sub = todo.add_subparsers(dest="action", required=True)

    add = todo_sub.add_parser("add", help="添加待办")
    add.add_argument("title", help="待办内容")
    add.add_argument("--due", default=None, help="截止时间")
    add.add_argument("--priority", default="medium", choices=["high", "medium", "low"])

    lst = todo_sub.add_parser("list", help="查看待办")
    lst.add_argument("--status", default=None, choices=["pending", "done"])
    lst.add_argument("--date", default=None, help="按截止日期筛选 YYYY-MM-DD")

    done = todo_sub.add_parser("done", help="标记完成")
    done.add_argument("id", type=int)
    delete = todo_sub.add_parser("delete", help="删除待办")
    delete.add_argument("id", type=int)
    todo_sub.add_parser("stats", help="统计")

    # ----- ledger -----
    ledger = subparsers.add_parser("ledger", help="记账统计")
    ledger_sub = ledger.add_subparsers(dest="action", required=True)

    add_l = ledger_sub.add_parser("add", help="记录收支")
    add_l.add_argument("note", help="说明")
    add_l.add_argument("amount", type=float, help="金额（正=收入，负=支出）")
    add_l.add_argument("--category", default=None, help="分类")
    add_l.add_argument("--type", default=None, choices=["income", "expense"], dest="tx_type")

    lst_l = ledger_sub.add_parser("list", help="查看明细")
    lst_l.add_argument("--category", default=None)
    lst_l.add_argument("--month", default=None, help="月份 YYYY-MM")

    stats_l = ledger_sub.add_parser("stats", help="统计")
    stats_l.add_argument("--month", default=None, help="月份 YYYY-MM")

    del_l = ledger_sub.add_parser("delete", help="删除记录")
    del_l.add_argument("id", type=int)

    # ----- remind -----
    remind = subparsers.add_parser("remind", help="定时提醒")
    remind_sub = remind.add_subparsers(dest="action")

    add_r = remind_sub.add_parser("add", help="创建提醒")
    add_r.add_argument("text", help='自然语言描述，如 "明天上午9点 开会"')
    remind_sub.add_parser("list", help="查看提醒")
    del_r = remind_sub.add_parser("delete", help="删除提醒")
    del_r.add_argument("id", type=int)
    tog_r = remind_sub.add_parser("toggle", help="启用/暂停")
    tog_r.add_argument("id", type=int)

    return parser


def main():
    # 预处理：支持 "remind <描述>" 快捷方式（自动转为 add）
    argv = sys.argv[1:]
    for i, arg in enumerate(argv):
        if arg == "remind" and i + 1 < len(argv) and argv[i + 1] not in ("add", "list", "delete", "toggle"):
            argv.insert(i + 1, "add")
            break
    sys.argv = [sys.argv[0]] + argv

    parser = build_parser()
    args = parser.parse_args()

    storage = Storage()
    todo_mgr = TodoManager(storage)
    ledger_mgr = LedgerManager(storage)
    remind_mgr = ReminderManager(storage)

    # ---- todo ----
    if args.module == "todo":
        if args.action == "add":
            print(todo_mgr.add(args.title, args.priority, args.due))
        elif args.action == "list":
            print(todo_mgr.list(args.status, args.date))
        elif args.action == "done":
            print(todo_mgr.done(args.id))
        elif args.action == "delete":
            print(todo_mgr.delete(args.id))
        elif args.action == "stats":
            print(todo_mgr.stats())

    # ---- ledger ----
    elif args.module == "ledger":
        if args.action == "add":
            print(ledger_mgr.add(args.note, args.amount, args.category, args.tx_type))
        elif args.action == "list":
            print(ledger_mgr.list(args.category, args.month))
        elif args.action == "stats":
            print(ledger_mgr.stats(args.month))
        elif args.action == "delete":
            print(ledger_mgr.delete(args.id))

    # ---- remind ----
    elif args.module == "remind":
        if args.action == "add":
            print(remind_mgr.add(args.text))
        elif args.action == "list":
            print(remind_mgr.list())
        elif args.action == "delete":
            print(remind_mgr.delete(args.id))
        elif args.action == "toggle":
            print(remind_mgr.toggle(args.id))
        elif args.action is None:
            parser.parse_args(["remind", "--help"])


if __name__ == "__main__":
    main()
