from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from bot.config import set_reminder_time
# 导入待办事项业务逻辑接口
from modules.todo import service as todo_service


async def handle_message(update: Update, context: CallbackContext):
    """处理用户消息的异步函数"""
    message = update.effective_message
    chat_id = update.effective_chat.id
    text = message.text.strip()
    
    # 判断是否为完成任务的指令
    if text.lower().startswith("done"):
        parts = text.split()
        if len(parts) != 2:
            await message.reply_text(
                "格式错误，请使用：done todo_id",
                parse_mode=ParseMode.HTML
            )
            return
        try:
            todo_id = int(parts[1])
            if todo_service.complete_todo(todo_id):
                await message.reply_text(
                    f"✅ 任务 <code>{todo_id}</code> 已标记为完成",
                    parse_mode=ParseMode.HTML
                )
            else:
                await message.reply_text(
                    "❌ 任务不存在或已完成",
                    parse_mode=ParseMode.HTML
                )
        except ValueError:
            await message.reply_text(
                "❌ 任务编号应为数字",
                parse_mode=ParseMode.HTML
            )
    
    # 判断是否为删除任务的指令
    elif text.lower().startswith("delete"):
        parts = text.split()
        if len(parts) != 2:
            await message.reply_text(
                "格式错误，请使用：delete todo_id",
                parse_mode=ParseMode.HTML
            )
            return
        try:
            todo_id = int(parts[1])
            if todo_service.delete_todo(todo_id):
                await message.reply_text(
                    f"🗑 任务 <code>{todo_id}</code> 已删除",
                    parse_mode=ParseMode.HTML
                )
            else:
                await message.reply_text(
                    "❌ 任务不存在",
                    parse_mode=ParseMode.HTML
                )
        except ValueError:
            await message.reply_text(
                "❌ 任务编号应为数字",
                parse_mode=ParseMode.HTML
            )
    
    # 判断是否为修改提醒时间的指令
    elif text.lower().startswith("change time"):
        parts = text.split(maxsplit=2)
        if len(parts) < 3:
            await message.reply_text(
                "格式错误，请使用：change time HH:MM",
                parse_mode=ParseMode.HTML
            )
            return
        new_time = parts[2].strip()
        if set_reminder_time(new_time):
            await message.reply_text(
                f"⏰ 提醒时间已更新为 <code>{new_time}</code>",
                parse_mode=ParseMode.HTML
            )
        else:
            await message.reply_text(
                "❌ 时间格式错误，请使用 HH:MM 格式",
                parse_mode=ParseMode.HTML
            )
    
    # 新增：修改任务截止时间的指令
    elif text.lower().startswith("change endtime"):
        # 格式示例：change endtime 1 2025-03-01 12:00
        command_args = text[len("change endtime"):].strip()
        parts = command_args.split(None, 1)
        if len(parts) < 2:
            await message.reply_text(
                "格式错误，请使用：change endtime todo_id YYYY-MM-DD HH:MM",
                parse_mode=ParseMode.HTML
            )
            return
        try:
            todo_id = int(parts[0])
        except ValueError:
            await message.reply_text(
                "任务编号应为数字",
                parse_mode=ParseMode.HTML
            )
            return
        new_end_time_str = parts[1]
        try:
            if todo_service.modify_end_time(todo_id, new_end_time_str):
                await message.reply_text(
                    f"✅ 任务 <code>{todo_id}</code> 截止时间已更新为 <code>{new_end_time_str}</code>",
                    parse_mode=ParseMode.HTML
                )
            else:
                await message.reply_text(
                    "❌ 任务不存在",
                    parse_mode=ParseMode.HTML
                )
        except ValueError as e:
            await message.reply_text(
                f"❌ {str(e)}",
                parse_mode=ParseMode.HTML
            )
    
    # 如果不匹配上述指令，则视为任务创建
    else:
        try:
            todo = todo_service.create_todo(text)
            response = (
                f"✅ 任务创建成功！\n"
                f"📌 任务编号：<code>{todo.todo_id}</code>\n"
                f"📝 任务内容：{todo.todo_name}\n"
                f"⏱ 创建时间：{todo.create_time.strftime('%Y-%m-%d %H:%M')}"
            )
            if todo.end_time:
                response += f"\n⏰ 截止时间：{todo.end_time.strftime('%Y-%m-%d %H:%M')}"
            
            await message.reply_text(
                response,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            await message.reply_text(
                f"❌ {str(e)}",
                parse_mode=ParseMode.HTML
            ) 