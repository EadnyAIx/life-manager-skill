"""待办管理模块。"""

from datetime import datetime

from storage import Storage


PRIORITY_LABEL = {"high": "高", "medium": "中", "low": "低"}
STATUS_LABEL = {"pending": "待办", "done": "已完成"}


class TodoManager:
    """待办事项管理。"""

    def __init__(self, storage: Storage):
        self.storage = storage

    def add(self, title: str, priority: str = "medium", due_date: str = None) -> str:
        """添加待办。"""
        if not title.strip():
            return "❌ 待办内容不能为空"
        if priority not in PRIORITY_LABEL:
            priority = "medium"
        todo_id = self.storage.add_todo(title.strip(), priority, due_date)
        return f"✅ 已添加待办 #{todo_id}: {title} (优先级:{PRIORITY_LABEL[priority]})"

    def list(self, status: str = None, due_date: str = None) -> str:
        """查看待办。"""
        todos = self.storage.list_todos(status=status, due_date=due_date)
        if not todos:
            return "📋 暂无待办事项"
        lines = ["📋 待办列表:"]
        for t in todos:
            mark = "✅" if t["status"] == "done" else "⬜"
            prio = PRIORITY_LABEL.get(t["priority"], t["priority"])
            due = f" (截止:{t['due_date']})" if t["due_date"] else ""
            lines.append(f"  {mark} #{t['id']} [{prio}] {t['title']}{due}")
        return "\n".join(lines)

    def done(self, todo_id: int) -> str:
        """标记完成。"""
        if self.storage.update_todo_status(todo_id, "done"):
            return f"✅ 待办 #{todo_id} 已完成"
        return f"❌ 未找到待办 #{todo_id}"

    def delete(self, todo_id: int) -> str:
        """删除待办。"""
        if self.storage.delete_todo(todo_id):
            return f"🗑️ 已删除待办 #{todo_id}"
        return f"❌ 未找到待办 #{todo_id}"

    def stats(self) -> str:
        """统计概览。"""
        s = self.storage.todo_stats()
        return (
            f"📊 待办统计:\n"
            f"  总计: {s['total']}\n"
            f"  已完成: {s['done']}\n"
            f"  待办中: {s['pending']}\n"
            f"  已逾期: {s['overdue']}"
        )
