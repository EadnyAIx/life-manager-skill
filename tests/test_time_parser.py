"""time_parser 单元测试。"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from time_parser import parse_time, _cn_to_int


def test_cn_to_int():
    assert _cn_to_int("三") == 3
    assert _cn_to_int("十二") == 12
    assert _cn_to_int("二十五") == 25
    assert _cn_to_int("7") == 7


def test_absolute_datetime():
    r = parse_time("2026-09-01 09:30")
    assert r["type"] == "at"
    assert r["datetime"].year == 2026
    assert r["datetime"].month == 9
    assert r["datetime"].hour == 9
    assert r["datetime"].minute == 30


def test_relative_days():
    now = datetime(2026, 9, 1, 12, 0)
    r = parse_time("明天上午9点", now=now)
    assert r["type"] == "at"
    assert r["datetime"].day == 2
    assert r["datetime"].hour == 9

    r2 = parse_time("后天 18:00", now=now)
    assert r2["datetime"].day == 3
    assert r2["datetime"].hour == 18


def test_relative_duration():
    now = datetime(2026, 9, 1, 12, 0)
    r = parse_time("3小时后", now=now)
    assert r["datetime"].hour == 15
    r2 = parse_time("2天后", now=now)
    assert r2["datetime"].day == 3


def test_weekly_cron():
    r = parse_time("每周五下午 写周报")
    assert r["type"] == "cron"
    assert r["cron"].endswith("* * 5")
    assert "14" in r["cron"]  # 下午 -> 14点


def test_daily_cron():
    r = parse_time("每天早上9点")
    assert r["type"] == "cron"
    assert r["cron"] == "0 9 * * *"


def test_weekday():
    now = datetime(2026, 9, 1, 12, 0)  # 周二
    r = parse_time("下周一 10:00", now=now)
    assert r["type"] == "at"
    assert r["datetime"].weekday() == 0  # 周一


def test_time_only():
    now = datetime(2026, 9, 1, 8, 0)
    r = parse_time("09:00", now=now)
    assert r["datetime"].hour == 9
    # 若时间已过，则推到明天
    now2 = datetime(2026, 9, 1, 10, 0)
    r2 = parse_time("09:00", now=now2)
    assert r2["datetime"].day == 2
