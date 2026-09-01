"""自然语言时间解析器：把中文/英文时间描述解析为具体日期时间或 cron 表达式。"""

import re
from datetime import datetime, timedelta


# 中文数字
_CN_NUMS = {"零": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4,
            "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
_CN_WEEK = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "日": 7, "天": 7}


def _cn_to_int(s: str) -> int:
    """中文数字转整数，支持一至九十九（如：三、十二、二十、二十五）。"""
    if s.isdigit():
        return int(s)
    if "十" in s:
        parts = s.split("十")
        tens = _CN_NUMS.get(parts[0], 1) if parts[0] else 1
        ones = _CN_NUMS.get(parts[1], 0) if len(parts) > 1 and parts[1] else 0
        return tens * 10 + ones
    return _CN_NUMS.get(s, 0)


def parse_time(text: str, now: datetime = None) -> dict:
    """解析自然语言时间描述。

    Args:
        text: 时间描述文本，如 "明天上午9点"、"每周五下午"、"3小时后"、"2026-09-01 09:00"
        now: 当前时间（默认取系统时间）

    Returns:
        dict: {"datetime": datetime 或 None, "cron": str 或 None, "type": "at"|"cron", "raw": str}
    """
    now = now or datetime.now()
    text = text.strip().lower()

    # 1. 绝对时间: YYYY-MM-DD [HH:MM]
    m = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})(?:\s+(\d{1,2})[:：](\d{1,2}))?", text)
    if m:
        try:
            dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)),
                          int(m.group(4) or 0), int(m.group(5) or 0))
            return {"datetime": dt, "cron": None, "type": "at", "raw": text}
        except ValueError:
            pass

    # 2. 周期提醒: 每周X / 每天 / 每月X日
    m = re.search(r"每(周|天|月)?([一二三四五六日天]|天)?(?:早上|上午|中午|下午|晚上)?\s*(\d{1,2})?[:：]?(\d{1,2})?", text)
    if "每周" in text or "每天" in text or "每" in text:
        if "每周" in text:
            wd_match = re.search(r"每周([一二三四五六日天])", text)
            if wd_match:
                wd = _CN_WEEK.get(wd_match.group(1), 1)
                hour, minute = _extract_hhmm(text)
                return {"datetime": None, "cron": f"{minute} {hour} * * {wd}", "type": "cron", "raw": text}
        if "每天" in text:
            hour, minute = _extract_hhmm(text)
            return {"datetime": None, "cron": f"{minute} {hour} * * *", "type": "cron", "raw": text}

    # 3. 相对时间: N小时后 / N分钟前 / 3天后
    m = re.search(r"(\d+|[一二两三四五六七八九十]+)\s*(小时|分钟|分钟|天|周)后", text)
    if m:
        n = _cn_to_int(m.group(1))
        unit = m.group(2)
        if "小时" in unit:
            dt = now + timedelta(hours=n)
        elif "分钟" in unit:
            dt = now + timedelta(minutes=n)
        elif "天" in unit:
            dt = now + timedelta(days=n)
        elif "周" in unit:
            dt = now + timedelta(weeks=n)
        else:
            dt = now
        return {"datetime": dt, "cron": None, "type": "at", "raw": text}

    # 4. 相对日期: 今天/明天/后天/昨天 + 时间
    day_offset = None
    if "大后天" in text:
        day_offset = 3
    elif "后天" in text:
        day_offset = 2
    elif "明天" in text or "明日" in text:
        day_offset = 1
    elif "今天" in text or "今日" in text:
        day_offset = 0
    elif "昨天" in text:
        day_offset = -1

    if day_offset is not None:
        hour, minute = _extract_hhmm(text)
        dt = (now + timedelta(days=day_offset)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        return {"datetime": dt, "cron": None, "type": "at", "raw": text}

    # 5. 星期: 下周一 / 周X
    m = re.search(r"(?:下周|下个)?周([一二三四五六日天])", text)
    if m:
        wd = _CN_WEEK.get(m.group(1), 1)
        # 计算到下一个目标星期的天数
        days_ahead = (wd - 1 - now.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7  # 今天就是目标星期时，推到下周
        target = now + timedelta(days=days_ahead)
        hour, minute = _extract_hhmm(text)
        target = target.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return {"datetime": target, "cron": None, "type": "at", "raw": text}

    # 6. 仅时间: HH:MM（默认今天，过了则明天）
    m = re.search(r"(?:早上|上午|中午|下午|晚上)?\s*(\d{1,2})[:：](\d{1,2})", text)
    if m:
        hour, minute = int(m.group(1)), int(m.group(2))
        dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if dt <= now:
            dt += timedelta(days=1)
        return {"datetime": dt, "cron": None, "type": "at", "raw": text}

    # 无法解析
    return {"datetime": None, "cron": None, "type": "unknown", "raw": text}


def _extract_hhmm(text: str) -> tuple:
    """从文本中提取小时和分钟，无数字时按时段默认（早上9点/中午12点/下午14点/晚上20点）。"""
    m = re.search(r"(?:早上|上午|中午|下午|晚上)?\s*(\d{1,2})[:：]?(\d{1,2})?", text)
    if m and m.group(1):
        hour = int(m.group(1))
        minute = int(m.group(2)) if m.group(2) else 0
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return hour, minute

    # 无具体数字，按时段默认
    if "下午" in text:
        return 14, 0
    if "晚上" in text:
        return 20, 0
    if "中午" in text:
        return 12, 0
    return 9, 0


def format_datetime(dt: datetime) -> str:
    """格式化日期时间为易读文本。"""
    return dt.strftime("%Y-%m-%d %H:%M")
