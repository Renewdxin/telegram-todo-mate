from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext
import logging
import re

from bot.config import set_reminder_time
# 导入待办事项业务逻辑接口
from modules.todo import service as todo_service
from modules.link.service import LinkService
from modules.link.ai_service import GrokAIService

# 初始化服务
link_service = LinkService()
ai_service = GrokAIService()

async def handle_message(update: Update, context: CallbackContext):
    """处理用户消息的异步函数"""
    message = update.effective_message
    chat_id = update.effective_chat.id
    text = message.text.strip()
    
    # 检查是否包含URL
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    if re.search(url_pattern, text):
        response = link_service.save_link(chat_id, text)
        await message.reply_text(
            response,
            parse_mode=ParseMode.HTML
        )
        return

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
                "❌ 任务编号应为数字",
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
                    "❌ 操作失败",
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

async def handle_summarize_command(update: Update, context: CallbackContext):
    """处理 /summarize 命令，随机获取一个未读链接并生成摘要"""
    chat_id = update.effective_chat.id
    
    try:
        # 获取随机未读链接
        link_info = link_service.get_random_unread_link(chat_id)
        if "没有未读的链接" in link_info:
            await update.message.reply_text(link_info)
            return

        await update.message.reply_text(
            "🤖 正在生成摘要，请稍候...",
            parse_mode=ParseMode.HTML
        )

        # 调用AI服务生成摘要
        summary = await ai_service.generate_summary(link_info.url, "获取链接内容")  # TODO: 添加内容获取逻辑
        response = link_service.update_summary(link_info.id, summary)
        
        await update.message.reply_text(
            response,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ 生成摘要时发生错误: {str(e)}",
            parse_mode=ParseMode.HTML
        )

async def handle_explain_command(update: Update, context: CallbackContext):
    """处理 /explain 命令，解释指定链接内容"""
    if not context.args:
        await update.message.reply_text(
            "❌ 请提供要解释的链接\n例如：/explain https://example.com",
            parse_mode=ParseMode.HTML
        )
        return

    url = context.args[0]
    await update.message.reply_text(
        "🤖 正在生成解释，请稍候...",
        parse_mode=ParseMode.HTML
    )

    try:
        explanation = await ai_service.generate_explanation(url, "获取链接内容")  # TODO: 添加内容获取逻辑
        await update.message.reply_text(
            explanation,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ 生成解释时发生错误: {str(e)}",
            parse_mode=ParseMode.HTML
        )

async def handle_unread_command(update: Update, context: CallbackContext):
    """处理 /unread 命令，显示未读链接统计"""
    chat_id = update.effective_chat.id
    response = link_service.get_unread_summary(chat_id)
    await update.message.reply_text(
        response,
        parse_mode=ParseMode.HTML
    )

async def handle_read_command(update: Update, context: CallbackContext):
    """处理 /read 命令，将链接标记为已读"""
    if not context.args:
        await update.message.reply_text(
            "❌ 请提供链接ID\n例如：/read 1",
            parse_mode=ParseMode.HTML
        )
        return

    try:
        link_id = int(context.args[0])
        response = link_service.mark_as_read(link_id)
        await update.message.reply_text(
            response,
            parse_mode=ParseMode.HTML
        )
    except ValueError:
        await update.message.reply_text(
            "❌ 无效的链接ID",
            parse_mode=ParseMode.HTML
        )

# 添加新的命令处理函数
async def handle_demo_command(update: Update, context: CallbackContext):
    """处理 /demo 命令"""
    if not update or not update.effective_message:
        logging.error("无效的更新对象或消息对象")
        return
        
    logging.info("执行 /demo 命令")
    todos = todo_service.get_all_todos()
    logging.info(f"获取到 {len(todos)} 个待办事项")
    formatted_list = todo_service.format_todo_list(todos, "all")
    
    await update.effective_message.reply_text(
        formatted_list,
        parse_mode=ParseMode.HTML
    )

async def handle_demoz_command(update: Update, context: CallbackContext):
    """处理 /demoz 命令"""
    if not update or not update.effective_message:
        logging.error("无效的更新对象或消息对象")
        return
        
    logging.info("执行 /demoz 命令")
    todos = todo_service.get_pending_todos()
    logging.info(f"获取到 {len(todos)} 个未完成待办事项")
    formatted_list = todo_service.format_todo_list(todos, "pending")
    
    await update.effective_message.reply_text(
        formatted_list,
        parse_mode=ParseMode.HTML
    ) 