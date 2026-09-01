"""ledger 模块单元测试。"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from storage import Storage
from ledger import LedgerManager


def make_ledger():
    tmp = tempfile.mkdtemp()
    storage = Storage(Path(tmp) / "test.db")
    return LedgerManager(storage)


def test_add_income_expense():
    mgr = make_ledger()
    out = mgr.add("工资", 8000, "收入", None)
    assert "收入" in out
    out2 = mgr.add("咖啡", -15, "餐饮", None)
    assert "支出" in out2


def test_stats():
    mgr = make_ledger()
    mgr.add("工资", 10000, "收入", None)
    mgr.add("餐饮", -100, "餐饮", None)
    mgr.add("交通", -50, "交通", None)
    stats = mgr.stats()
    assert "总收入: 10000.00" in stats
    assert "总支出: 150.00" in stats
    assert "结余: 9850.00" in stats
    assert "餐饮" in stats


def test_invalid_amount():
    mgr = make_ledger()
    out = mgr.add("测试", "abc")
    assert "金额格式不正确" in out
