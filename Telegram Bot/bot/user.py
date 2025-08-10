import datetime, asyncio
from yt_dlp import YoutubeDL
from telegram import (
    Update, InlineKeyboardButton,
    InlineKeyboardMarkup,InputFile )
from telegram.ext import ContextTypes
from bot.downloader import download_worker
from bot.localization import get_text
from bot.config import (
    LOGS_DIR, TEST_URLS, INSTAGRAM_COOKIES,
    COOKIE_AGE_LIMIT, BASE_DIR, ADMIN_ID,
    ADMIN_ACTIONS, FEEDBACK_LOG, REPORT_LOG, HISTORY_LOG,
    MESSAGES_LOG, ERRORS_LOG, GIF_PATH )
from bot.utils import (
    send_admin_notification, log_user,
    check_cookie_freshness, too_fast,
    last_command_time, user_lang, logger,
    queue, user_queues )


async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id  # Получаем ID до проверки аргументов
    
    if len(context.args) == 0:
        await update.message.reply_text(get_text(user_id, "feedback_format_error"))
        return
    
    text = ' '.join(context.args)
    username = user.username or "N/A"
    
    with open(FEEDBACK_LOG, "a") as f:
        f.write(f"{datetime.datetime.now()} | {user_id} | {text}\n")
    
    await send_admin_notification(
        context=context,
        action="NEW_FEEDBACK",
        details=get_text(user_id, "new_feedback").format(
            username=username,
            user_id=user_id,
            text=text
        ),
        user_id=ADMIN_ID  # Передаем явно
    )
    
    await update.message.reply_text(get_text(user_id, "feedback_sent"))
   

async def handle_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id  # Получаем ID здесь
    
    if len(context.args) == 0:
        await update.message.reply_text(get_text(user_id, "report_format_error"))
        return
    
    text = ' '.join(context.args)
    username = user.username or "N/A"
    
    with open(REPORT_LOG, "a") as f:
        f.write(f"{datetime.datetime.now()} | {user_id} | {text}\n")
    
    await send_admin_notification(
        context=context,
        action="NEW_REPORT",
        details=get_text(user_id, "new_report").format(
            username=username,
            user_id=user_id,
            text=text
        ),
        user_id=ADMIN_ID  # Явная передача
    )
    
    await update.message.reply_text(get_text(user_id, "report_sent"))

async def show_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    total = len(queue)
    user_count = len(user_queues[user_id])
    await update.message.reply_text(
        get_text(user_id, "queue_status").format(count=user_count, total=total))

async def check_service(service_name: str, url: str) -> tuple[str, bool]:
    ydl_opts = {
        'quiet': True,
        'socket_timeout': 10,
        'extract_flat': True,
        'cookiefile': INSTAGRAM_COOKIES if "instagram" in url else None,
        'ssl_version': 'TLSv1_2',
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            await asyncio.to_thread(ydl.extract_info, url, download=False)
        return (service_name, True)
    except Exception as e:
        logger.error(f"Service check failed for {service_name}: {str(e)}")
        return (service_name, False)

async def check_services_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = {}
    
    if not check_cookie_freshness():
        msg = get_text(ADMIN_ID, "cookie_expired")
        await send_admin_notification(
            context=context,
            action="COOKIE_EXPIRED",
            details=msg,
            user_id=ADMIN_ID
        )

    tasks = [
        asyncio.create_task(check_service(service, url))
        for service, url in TEST_URLS.items()
    ]
    
    done, pending = await asyncio.wait(tasks, timeout=15)
    
    for task in done:
        try:
            service_name, result = task.result()
            status[service_name] = result
        except Exception as e:
            logger.error(f"Error processing task: {str(e)}")

    status_text = get_text(update.effective_user.id, "service_status").format(
        yt="✅" if status.get("youtube", False) else "❌",
        yt_shorts="✅" if status.get("youtube_shorts", False) else "❌",
        tt="✅" if status.get("tiktok", False) else "❌",
        ig="✅" if status.get("instagram", False) else "❌"
    )
    
    await update.message.reply_text(
        get_text(update.effective_user.id, "service_status_header").format(status_text=status_text)
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.language_code in ['tk', 'ru', 'en']:
        user_lang[user.id] = user.language_code
    if too_fast(update.effective_user.id): 
        return
    log_user(update)
    
    try:
        # Отправка MP4 как анимации с текстом в подписи
        with open(GIF_PATH, "rb") as video_file:
            await update.message.reply_animation(
                animation=InputFile(video_file),
                caption=get_text(update.effective_user.id, "start"),
                write_timeout=30  # Увеличиваем таймаут для больших файлов
            )
            
    except FileNotFoundError:
        logger.error("Start MP4 file not found!")
        await update.message.reply_text(get_text(update.effective_user.id, "start"))
        
    except Exception as e:
        logger.error(f"Error sending start animation: {str(e)}")
        await update.message.reply_text(get_text(update.effective_user.id, "start"))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_text(update.effective_user.id, "help"))

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Türkmençe 🇹🇲", callback_data="lang_tk"),
            InlineKeyboardButton("Русский 🇷🇺", callback_data="lang_ru"),
            InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")
        ]
    ]
    await update.message.reply_text(
        get_text(update.effective_user.id, "lang_select"),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

