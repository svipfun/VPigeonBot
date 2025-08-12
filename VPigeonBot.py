import logging
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# 配置日志
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# 替换为您的实际值
TOKEN = '自行获取'  # 从 BotFather 获取
OWNER_ID = 自行获取  # 您的 Telegram User ID，从 @userinfobot 获取

# 数据库文件
DB_FILE = 'VPigeonBot.db'

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS mappings 
                      (message_id INTEGER PRIMARY KEY, original_chat_id INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS blocked 
                      (user_id INTEGER PRIMARY KEY)''')
    conn.commit()
    conn.close()

def get_mapping(message_id: int) -> int | None:
    """从数据库获取映射"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT original_chat_id FROM mappings WHERE message_id = ?', (message_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def insert_mapping(message_id: int, original_chat_id: int):
    """插入映射到数据库"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO mappings (message_id, original_chat_id) VALUES (?, ?)',
                   (message_id, original_chat_id))
    conn.commit()
    conn.close()

def get_blocked() -> set:
    """获取屏蔽列表"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM blocked')
    results = cursor.fetchall()
    conn.close()
    return {row[0] for row in results}

def insert_blocked(user_id: int):
    """添加屏蔽用户"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO blocked (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def remove_blocked(user_id: int):
    """移除屏蔽用户"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM blocked WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

async def start(update: Update, context: CallbackContext):
    """处理 /start 命令"""
    if update.message.chat.id != OWNER_ID:
        await update.message.reply_text("Welcome! I will reply as soon as I receive your message. Thank you!")
    else:
        await update.message.reply_text("欢迎主人！使用 /block <user_id> 屏蔽用户，/unblock <user_id> 解除，/listblocked 查看列表。")
async def help(update: Update, context: CallbackContext):
    """处理 /help 命令"""
    if update.message.chat.id != OWNER_ID:
        await update.message.reply_text("You can contact me through this bot.")
    else:
        await update.message.reply_text("欢迎主人！使用 /block <user_id> 屏蔽用户，/unblock <user_id> 解除，/listblocked 查看列表。")
async def block(update: Update, context: CallbackContext):
    """处理 /block 命令"""
    if update.message.chat.id != OWNER_ID:
        #return  # 非主人忽略，不响应
        await update.message.reply_text("You not admin！")
        return  # 非主人忽略，不响应
    if not context.args:
        await update.message.reply_text("用法: /block <user_id>")
        return
    try:
        user_id = int(context.args[0])
        insert_blocked(user_id)
        await update.message.reply_text(f"已屏蔽用户 {user_id}")
    except ValueError:
        await update.message.reply_text("user_id 必须是数字")

async def unblock(update: Update, context: CallbackContext):
    """处理 /unblock 命令"""
    if update.message.chat.id != OWNER_ID:
        #return  # 非主人忽略，不响应
        await update.message.reply_text("You not admin！")
        return  # 非主人忽略，不响应
    if not context.args:
        await update.message.reply_text("用法: /unblock <user_id>")
        return
    try:
        user_id = int(context.args[0])
        remove_blocked(user_id)
        await update.message.reply_text(f"已解除屏蔽用户 {user_id}")
    except ValueError:
        await update.message.reply_text("user_id 必须是数字")

async def listblocked(update: Update, context: CallbackContext):
    """处理 /listblocked 命令"""
    if update.message.chat.id != OWNER_ID:
        await update.message.reply_text("You not admin！")
        return  # 非主人忽略，不响应
    blocked = get_blocked()
    if not blocked:
        await update.message.reply_text("没有屏蔽用户")
    else:
        text = "屏蔽用户列表:\n" + "\n".join(str(uid) for uid in blocked)
        await update.message.reply_text(text)

async def message_handler(update: Update, context: CallbackContext):
    """处理所有消息"""
    message = update.message
    chat_id = message.chat.id
    user = message.from_user

    if chat_id == OWNER_ID:
        # 主人回复消息
        if message.reply_to_message:
            reply_to_id = message.reply_to_message.message_id
            original_chat_id = get_mapping(reply_to_id)
            if original_chat_id:
                try:
                    if message.text:
                        await context.bot.send_message(original_chat_id, text=message.text)
                    elif message.photo:
                        await context.bot.send_photo(original_chat_id, photo=message.photo[-1].file_id, caption=message.caption)
                    elif message.voice:
                        await context.bot.send_voice(original_chat_id, voice=message.voice.file_id, caption=message.caption)
                    elif message.video:
                        await context.bot.send_video(original_chat_id, video=message.video.file_id, caption=message.caption)
                    elif message.document:
                        await context.bot.send_document(original_chat_id, document=message.document.file_id, caption=message.caption)
                    elif message.sticker:
                        await context.bot.send_sticker(original_chat_id, sticker=message.sticker.file_id)
                    # 可以添加更多类型，如 audio, location 等
                    await message.reply_text("已转发给消息来源者！")
                except Exception as e:
                    logger.error(f"转发失败: {e}")
                    await message.reply_text(f"转发失败: {str(e)}")
            else:
                await message.reply_text("无法找到原用户，请检查是否是回复我的转发消息。")
        else:
            await update.message.reply_text("请直接在原消息上回复，我会转发给消息来源者。")
    else:
        # 陌生人消息，先检查屏蔽
        blocked = get_blocked()
        if user.id in blocked:
            logger.info(f"忽略屏蔽用户 {user.id} 的消息")
            return
        # 转发给主人，用户名加 @ 符号
        username = f"@{user.username}" if user.username else "无用户名"
        info = f"来自 {username} (ID: {user.id}, 姓名: {user.first_name or '未知'})"
        forwarded = None
        try:
            if message.text:
                forwarded = await context.bot.send_message(OWNER_ID, text=f"{info}\n{message.text}")
            elif message.photo:
                forwarded = await context.bot.send_photo(OWNER_ID, photo=message.photo[-1].file_id, caption=f"{info}\n{message.caption or ''}")
            elif message.voice:
                forwarded = await context.bot.send_voice(OWNER_ID, voice=message.voice.file_id, caption=f"{info}\n{message.caption or ''}")
            elif message.video:
                forwarded = await context.bot.send_video(OWNER_ID, video=message.video.file_id, caption=f"{info}\n{message.caption or ''}")
            elif message.document:
                forwarded = await context.bot.send_document(OWNER_ID, document=message.document.file_id, caption=f"{info}\n{message.caption or ''}")
            elif message.sticker:
                forwarded = await context.bot.send_sticker(OWNER_ID, sticker=message.sticker.file_id)
                # Sticker 无 caption，所以单独发送 info
                await context.bot.send_message(OWNER_ID, text=info)
            # 可以添加更多类型
            if forwarded:
                insert_mapping(forwarded.message_id, chat_id)
                logger.info(f"转发消息成功，映射: {forwarded.message_id} -> {chat_id}")
        except Exception as e:
            logger.error(f"转发失败: {e}")

def main():
    """主函数，启动机器人"""
    init_db()  # 初始化数据库
    application = Application.builder().token(TOKEN).build()

    # 添加处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("block", block))
    application.add_handler(CommandHandler("unblock", unblock))
    application.add_handler(CommandHandler("listblocked", listblocked))
    # 对于其他未定义命令，默认不响应
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, message_handler))

    # 本地测试用 polling，服务器部署可改为 webhook
    application.run_polling()

if __name__ == '__main__':
    main()