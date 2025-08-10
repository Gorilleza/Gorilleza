import os, asyncio, logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot.admin import *
from bot.user import *
from bot.utils import *
from bot.downloader import *
from bot.config import *
from bot.localization import get_text


def main():
    setup_logging()
    try:
        load_bans()
    except Exception as e:
        logger.critical(f"CRITICAL ERROR LOADING BANS: {str(e)}")
    
    if os.path.exists(PENDING_QUEUE_FILE):
        with open(PENDING_QUEUE_FILE, "r") as f:
            for line in f:
                task = json.loads(line)
                queue.append((task["url"], task["user_id"]))
        os.remove(PENDING_QUEUE_FILE)
    
    if ADMIN_ID == 0:
        logger.warning("ADMIN_ID not set! Admin features disabled")
    
    if not os.access(LOGS_DIR, os.W_OK):
        logger.critical("Нет прав на запись в папку specified_logs!")
        exit(1)

    app = ApplicationBuilder().token(TOKEN).post_shutdown(on_shutdown).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("lang", lang_command))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("feedback", handle_feedback))
    app.add_handler(CommandHandler("report", handle_report))
    app.add_handler(CommandHandler("queue", show_queue))
    app.add_handler(CommandHandler("status", check_services_status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(format_handler, pattern="^format_"))
    app.add_handler(CallbackQueryHandler(quality_handler, pattern="^quality_"))
    app.add_handler(CallbackQueryHandler(lang_callback, pattern=r"^lang_"))
    loop = asyncio.get_event_loop()
    loop.create_task(download_worker())
    loop.create_task(cleanup_task())
    app.run_polling()

if __name__ == "__main__":
    main()