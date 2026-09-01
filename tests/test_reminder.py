"""reminder 模块单元测试。"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from storage import Storage
from reminder import ReminderManager


def make_reminder():
    tmp = tempfile.mkdtemp()
    storage = Storage(Path(tmp) / "test.db")
    return ReminderManager(storage)


def test_add_at_reminder():
    mgr = make_reminder()
    out = mgr.add("明天上午9点 项目周会")
    assert "已创建" in out
    assert "一次性" in out


def test_add_cron_reminder():
    mgr = make_reminder()
    out = mgr.add("每周五下午 写周报")
    assert "已创建" in out
    assert "周期" in out


def test_unparseable():
    mgr = make_reminder()
    out = mgr.add("随便写点什么")
    assert "无法解析" in out


def test_list_toggle_delete():
    mgr = make_reminder()
    mgr.add("明天上午9点 开会")
    listing = mgr.list()
    assert "开会" in listing

    mgr.toggle(1)
    listing = mgr.list()
    assert "⏸️" in listing

    mgr.delete(1)
    listing = mgr.list()
    assert "暂无" in listing
