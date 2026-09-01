"""记账统计模块。"""

from datetime import datetime

from storage import Storage


DEFAULT_CATEGORIES = ["餐饮", "交通", "购物", "居住", "娱乐", "医疗", "教育", "收入", "其他"]


class LedgerManager:
    """收支记账与统计。"""

    def __init__(self, storage: Storage):
        self.storage = storage

    def add(self, note: str, amount: float, category: str = None, tx_type: str = None) -> str:
        """记录一笔收支。

        金额为正表示收入，为负表示支出；也可通过 --type 明确指定。
        """
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return "❌ 金额格式不正确"

        # 判定收支类型
        if tx_type:
            tx_type = "income" if tx_type in ("income", "收入", "in", "+") else "expense"
        else:
            tx_type = "income" if amount > 0 else "expense"

        category = category or ("收入" if tx_type == "income" else "其他")
        ledger_id = self.storage.add_ledger(abs(amount), category, note, tx_type)
        tag = "收入" if tx_type == "income" else "支出"
        return f"✅ 已记录{tag}: {note} {abs(amount):.2f}元 (分类:{category})"

    def list(self, category: str = None, month: str = None) -> str:
        """查看收支明细。"""
        entries = self.storage.list_ledger(category=category, month=month)
        if not entries:
            return "💳 暂无收支记录"
        lines = ["💳 收支明细:"]
        for e in entries:
            sign = "+" if e["tx_type"] == "income" else "-"
            lines.append(
                f"  #{e['id']} {e['created_at'][:16]} [{e['category']}] "
                f"{e['note']} {sign}{e['amount']:.2f}"
            )
        return "\n".join(lines)

    def stats(self, month: str = None) -> str:
        """月度统计。"""
        s = self.storage.ledger_stats(month=month)
        period = f"{month}" if month else "全部时间"
        lines = [
            f"📊 收支统计 ({period}):",
            f"  总收入: {s['income']:.2f} 元",
            f"  总支出: {s['expense']:.2f} 元",
            f"  结余: {s['balance']:.2f} 元",
        ]
        if s["breakdown"]:
            lines.append("  支出分类占比:")
            for b in s["breakdown"][:6]:
                bar = "█" * int(b["percent"] / 5)
                lines.append(f"    {b['category']}: {b['amount']:.2f}元 ({b['percent']}%) {bar}")
        return "\n".join(lines)

    def delete(self, ledger_id: int) -> str:
        """删除记录。"""
        if self.storage.delete_ledger(ledger_id):
            return f"🗑️ 已删除记录 #{ledger_id}"
        return f"❌ 未找到记录 #{ledger_id}"
