"""todo 模块单元测试。"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from storage import Storage
from todo import TodoManager


def make_todo():
    tmp = tempfile.mkdtemp()
    storage = Storage(Path(tmp) / "test.db")
    return TodoManager(storage)


def test_add_list_done_delete():
    mgr = make_todo()
    out = mgr.add("提交简历", "high", "2026-09-05")
    assert "已添加" in out

    listing = mgr.list()
    assert "提交简历" in listing

    mgr.done(1)
    listing = mgr.list()
    assert "✅" in listing

    mgr.delete(1)
    listing = mgr.list()
    assert "暂无" in listing


def test_stats():
    mgr = make_todo()
    mgr.add("任务A", "high", None)
    mgr.add("任务B", "low", None)
    mgr.done(1)
    stats = mgr.stats()
    assert "总计: 2" in stats
    assert "已完成: 1" in stats


def test_empty_title():
    mgr = make_todo()
    out = mgr.add("  ", "medium", None)
    assert "不能为空" in out
