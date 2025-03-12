import os
import sqlite3
import random
from datetime import datetime, timedelta, timezone
from pkg.plugin.context import *
from pkg.plugin.events import *
from pkg.platform.types import *
import asyncio
import json

# 创建UTC+8时区对象
china_tz = timezone(timedelta(hours=8))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "luck_records.db")

def init_db():
    """
    初始化数据库，如果 luck_records 表不存在，则创建。
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS luck_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            date TEXT NOT NULL,
            luck_value INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def get_today_luck(user_id: str) -> int:
    """
    查询用户今天的运势值，如果已经存在，则直接返回；否则生成一个并存储到数据库。
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    today_str = datetime.now(china_tz).strftime("%Y-%m-%d")

    # 先检查今天是否已经有记录
    c.execute(
        "SELECT luck_value FROM luck_records WHERE user_id = ? AND date = ?",
        (user_id, today_str)
    )
    row = c.fetchone()

    if row is not None:
        # 已有记录，直接返回
        luck_value = row[0]
        conn.close()
        return luck_value

    # 如果没有记录，则随机生成 0~100
    luck_value = random.randint(0, 100)
    c.execute(
        "INSERT INTO luck_records (user_id, date, luck_value) VALUES (?, ?, ?)",
        (user_id, today_str, luck_value)
    )
    conn.commit()
    conn.close()
    return luck_value

def get_all_luck_records(user_id: str):
    """
    获取该用户全部的运势记录，按日期降序。
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT date, luck_value FROM luck_records WHERE user_id = ? ORDER BY date DESC",
        (user_id,)
    )
    rows = c.fetchall()
    conn.close()
    return rows

def delete_today_luck(user_id: str) -> bool:
    """
    删除用户当天的运势记录。返回 True 表示删除成功，False 表示无记录。
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    today_str = datetime.now(china_tz).strftime("%Y-%m-%d")
    c.execute(
        "DELETE FROM luck_records WHERE user_id = ? AND date = ?",
        (user_id, today_str)
    )
    rowcount = c.rowcount
    conn.commit()
    conn.close()
    return rowcount > 0

def delete_all_luck(user_id: str) -> int:
    """
    删除用户所有运势记录，返回删除的条数。
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "DELETE FROM luck_records WHERE user_id = ?",
        (user_id,)
    )
    rowcount = c.rowcount
    conn.commit()
    conn.close()
    return rowcount

@register(name="LuckPlugin",
          description="测试运势的插件，使用/rp获取当日运势，并进行记录保存。",
          version="1.0",
          author="YourName")
class LuckPlugin(BasePlugin):

    def __init__(self, host: APIHost):
        # 如果需要一些状态或计时器，可以在这里初始化
        self.host = host

    async def initialize(self):
        # 插件启动时，先初始化数据库
        init_db()

    @handler(PersonMessageReceived)
    @handler(GroupMessageReceived)
    async def on_message(self, ctx: EventContext):
        """
        监听聊天事件，根据用户输入的命令来进行处理
        """
        msg = str(ctx.event.message_chain).strip()
        user_id = str(ctx.event.sender_id)   # 发送者 ID
        # group_id = str(ctx.event.launcher_id)  # 群号（如果需要，可以在群聊中做区分）

        if not msg:
            return  # 空消息则不处理

        parts = msg.split(maxsplit=1)
        cmd = parts[0].lstrip("/").lower()  # 去除命令中的 '/', 并转小写
        arg = parts[1].strip() if len(parts) > 1 else ""

        # === 命令：/rp ===
        if cmd == "rp":
            # 获取当天运势
            luck_value = get_today_luck(user_id)
            reply_text = f"今日人品（RP）值：{luck_value}"
            await ctx.reply(MessageChain([Plain(reply_text)]))
            return

        # === 命令：/rp记录 ===
        # 用户想查看自己所有的历史运势
        if cmd == "rp记录":
            all_records = get_all_luck_records(user_id)
            if not all_records:
                await ctx.reply(MessageChain([Plain("你还没有任何运势记录~")]))
                return

            report = ["你的运势记录（近到远）："]
            for row in all_records:
                date_str, val = row
                report.append(f"{date_str} => {val}")
            # 可以根据需要做分页、或只展示最近几条
            await ctx.reply(MessageChain([Plain("\n".join(report))]))
            return

        # === 命令：/rp删除 ===
        # 可选参数：today or all
        if cmd == "rp删除":
            if arg == "today":
                # 删除今日记录
                success = delete_today_luck(user_id)
                if success:
                    await ctx.reply(MessageChain([Plain("已删除你今天的运势记录")]))
                else:
                    await ctx.reply(MessageChain([Plain("你今天还没有运势记录，无需删除")]))
                return
            elif arg == "all":
                # 删除所有记录
                count = delete_all_luck(user_id)
                await ctx.reply(MessageChain([Plain(f"已删除你全部 {count} 条运势记录")]))
                return
            else:
                # 参数不正确时，可给一些提示
                tips = "用法示例：\n/rp删除 today  （删除今天的记录）\n/rp删除 all    （删除全部记录）"
                await ctx.reply(MessageChain([Plain(tips)]))
                return

    def __del__(self):
        pass
