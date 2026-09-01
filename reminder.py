"""定时提醒模块：解析自然语言时间并存储提醒任务。"""

from storage import Storage
from time_parser import parse_time, format_datetime


class ReminderManager:
    """定时提醒管理。"""

    def __init__(self, storage: Storage):
        self.storage = storage

    def add(self, text: str) -> str:
        """从自然语言描述创建提醒。

        例如: "明天上午9点 项目周会" / "每周五下午 写周报" / "3小时后 喝水"
        """
        if not text.strip():
            return "❌ 提醒内容不能为空"

        # 分离时间和内容：常见格式是 "时间 内容"
        parsed = parse_time(text)

        if parsed["type"] == "cron":
            schedule = parsed["cron"]
            schedule_type = "cron"
            desc = f"周期提醒: {parsed['raw']}"
        elif parsed["type"] == "at" and parsed["datetime"]:
            schedule = format_datetime(parsed["datetime"])
            schedule_type = "at"
            desc = f"一次性提醒: {schedule}"
        else:
            return f"❌ 无法解析时间: {text}（支持如: 明天上午9点 / 每周五下午 / 3小时后）"

        reminder_id = self.storage.add_reminder(text, schedule, schedule_type)
        return f"✅ 已创建{desc} (#{reminder_id}) 内容: {text}"

    def list(self) -> str:
        """查看所有提醒。"""
        reminders = self.storage.list_reminders()
        if not reminders:
            return "⏰ 暂无提醒"
        lines = ["⏰ 提醒列表:"]
        for r in reminders:
            on_off = "✅" if r["enabled"] else "⏸️"
            type_label = "周期" if r["schedule_type"] == "cron" else "一次性"
            lines.append(f"  {on_off} #{r['id']} [{type_label}] {r['schedule']} → {r['content']}")
        return "\n".join(lines)

    def delete(self, reminder_id: int) -> str:
        """删除提醒。"""
        if self.storage.delete_reminder(reminder_id):
            return f"🗑️ 已删除提醒 #{reminder_id}"
        return f"❌ 未找到提醒 #{reminder_id}"

    def toggle(self, reminder_id: int) -> str:
        """启用/暂停提醒。"""
        if self.storage.toggle_reminder(reminder_id):
            return f"🔄 已切换提醒 #{reminder_id} 状态"
        return f"❌ 未找到提醒 #{reminder_id}"
