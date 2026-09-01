"""SQLite 统一存储层：管理 todo / ledger / reminder 三类数据。"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path


DEFAULT_DB_PATH = Path(__file__).parent / "data" / "life.db"


class Storage:
    """SQLite 存储管理器，负责建表和基本 CRUD。"""

    def __init__(self, db_path: Path = None):
        self.db_path = Path(db_path or DEFAULT_DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()

    @contextmanager
    def _conn(self):
        """获取数据库连接（上下文管理器，自动提交/关闭）。"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_tables(self):
        """初始化数据表。"""
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    priority TEXT DEFAULT 'medium',
                    due_date TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    completed_at TEXT
                );

                CREATE TABLE IF NOT EXISTS ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    category TEXT DEFAULT '其他',
                    note TEXT DEFAULT '',
                    tx_type TEXT DEFAULT 'expense',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    schedule TEXT NOT NULL,
                    schedule_type TEXT DEFAULT 'at',
                    enabled INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_triggered TEXT
                );
                """
            )

    # ---------- Todo ----------
    def add_todo(self, title: str, priority: str, due_date: str) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO todos (title, priority, due_date) VALUES (?, ?, ?)",
                (title, priority, due_date),
            )
            return cur.lastrowid

    def list_todos(self, status: str = None, due_date: str = None) -> list:
        sql = "SELECT * FROM todos"
        conds, params = [], []
        if status:
            conds.append("status = ?")
            params.append(status)
        if due_date:
            conds.append("due_date = ?")
            params.append(due_date)
        if conds:
            sql += " WHERE " + " AND ".join(conds)
        sql += " ORDER BY CASE priority WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END, due_date"
        with self._conn() as conn:
            rows = conn.execute(sql, params).fetchall()
            return [dict(r) for r in rows]

    def update_todo_status(self, todo_id: int, status: str) -> bool:
        with self._conn() as conn:
            cur = conn.execute(
                "UPDATE todos SET status = ?, completed_at = ? WHERE id = ?",
                (status, datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status == "done" else None, todo_id),
            )
            return cur.rowcount > 0

    def delete_todo(self, todo_id: int) -> bool:
        with self._conn() as conn:
            cur = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
            return cur.rowcount > 0

    def todo_stats(self) -> dict:
        with self._conn() as conn:
            total = conn.execute("SELECT COUNT(*) c FROM todos").fetchone()["c"]
            done = conn.execute("SELECT COUNT(*) c FROM todos WHERE status='done'").fetchone()["c"]
            pending = conn.execute("SELECT COUNT(*) c FROM todos WHERE status='pending'").fetchone()["c"]
            today = datetime.now().strftime("%Y-%m-%d")
            overdue = conn.execute(
                "SELECT COUNT(*) c FROM todos WHERE status='pending' AND due_date IS NOT NULL AND due_date < ?",
                (today,),
            ).fetchone()["c"]
            return {"total": total, "done": done, "pending": pending, "overdue": overdue}

    # ---------- Ledger ----------
    def add_ledger(self, amount: float, category: str, note: str, tx_type: str) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO ledger (amount, category, note, tx_type) VALUES (?, ?, ?, ?)",
                (abs(amount), category, note, tx_type),
            )
            return cur.lastrowid

    def list_ledger(self, category: str = None, month: str = None) -> list:
        sql = "SELECT * FROM ledger"
        conds, params = [], []
        if category:
            conds.append("category = ?")
            params.append(category)
        if month:
            conds.append("substr(created_at, 1, 7) = ?")
            params.append(month)
        if conds:
            sql += " WHERE " + " AND ".join(conds)
        sql += " ORDER BY created_at DESC"
        with self._conn() as conn:
            rows = conn.execute(sql, params).fetchall()
            return [dict(r) for r in rows]

    def ledger_stats(self, month: str = None) -> dict:
        """按月统计收支和分类占比。"""
        sql_income = "SELECT COALESCE(SUM(amount), 0) s FROM ledger WHERE tx_type='income'"
        sql_expense = "SELECT COALESCE(SUM(amount), 0) s FROM ledger WHERE tx_type='expense'"
        params = ()
        if month:
            sql_income += " AND substr(created_at, 1, 7) = ?"
            sql_expense += " AND substr(created_at, 1, 7) = ?"
            params = (month, month)

        with self._conn() as conn:
            income = conn.execute(sql_income, params).fetchone()["s"]
            expense = conn.execute(sql_expense, params).fetchone()["s"]

            # 分类占比（支出）
            cats = conn.execute(
                "SELECT category, SUM(amount) s, COUNT(*) n FROM ledger WHERE tx_type='expense'"
                + (" AND substr(created_at, 1, 7) = ?" if month else "")
                + " GROUP BY category ORDER BY s DESC",
                (month,) if month else (),
            ).fetchall()

        total = expense if expense > 0 else 1
        breakdown = [
            {"category": r["category"], "amount": r["s"], "count": r["n"], "percent": round(r["s"] / total * 100, 1)}
            for r in cats
        ]
        return {
            "income": income,
            "expense": expense,
            "balance": income - expense,
            "breakdown": breakdown,
        }

    def delete_ledger(self, ledger_id: int) -> bool:
        with self._conn() as conn:
            cur = conn.execute("DELETE FROM ledger WHERE id = ?", (ledger_id,))
            return cur.rowcount > 0

    # ---------- Reminder ----------
    def add_reminder(self, content: str, schedule: str, schedule_type: str) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO reminders (content, schedule, schedule_type) VALUES (?, ?, ?)",
                (content, schedule, schedule_type),
            )
            return cur.lastrowid

    def list_reminders(self, enabled: bool = None) -> list:
        sql = "SELECT * FROM reminders"
        if enabled is not None:
            sql += " WHERE enabled = " + ("1" if enabled else "0")
        sql += " ORDER BY created_at DESC"
        with self._conn() as conn:
            rows = conn.execute(sql).fetchall()
            return [dict(r) for r in rows]

    def delete_reminder(self, reminder_id: int) -> bool:
        with self._conn() as conn:
            cur = conn.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
            return cur.rowcount > 0

    def toggle_reminder(self, reminder_id: int) -> bool:
        with self._conn() as conn:
            cur = conn.execute(
                "UPDATE reminders SET enabled = 1 - enabled WHERE id = ?", (reminder_id,)
            )
            return cur.rowcount > 0
