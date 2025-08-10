import os, re, json, time, logging
import datetime, asyncio, pyzipper, traceback
from logging.handlers import RotatingFileHandler
from collections import deque, defaultdict
from functools import wraps
from pathlib import Path
from telegram import (
    InlineKeyboardMarkup, InputFile,
    Update, InlineKeyboardButton ) 
from telegram.ext import ContextTypes
from bot.localization import TEXTS, get_text
from bot.config import (
    LOGS_DIR,
    ADMIN_ID, MAX_USER_QUEUE, COOKIE_AGE_LIMIT,
    INSTAGRAM_COOKIES, BASE_DIR, banned_users,
    user_lang, queue, user_queues, last_command_time,
    ADMIN_ACTIONS, USER_STATS_FILE, USER_STATES_FILE,
    FEEDBACK_LOG, REPORT_LOG, HISTORY_LOG,
    MESSAGES_LOG, ERRORS_LOG, LAST_LOG, PENDING_QUEUE_FILE,
    RATE_LIMITS, request_counters, last_request_time,
    MAX_GLOBAL_QUEUE )

def rate_limit(command_type="default"):
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id
            limits = RATE_LIMITS.get(command_type, RATE_LIMITS["default"])
            
            now = time.time()
            time_diff = now - last_request_time[user_id]
            
            if time_diff > limits["interval"]:
                request_counters[user_id][command_type] = 0
                last_request_time[user_id] = now
            
            if request_counters[user_id][command_type] >= limits["requests"]:
                await update.message.reply_text(
                    get_text(user_id, "rate_limit").format(
                        timeout=int(limits["interval"] - time_diff)
                ))
                log_admin_action(
                    admin_id=0,
                    action="RATE_LIMIT_TRIGGERED",
                    details={
                        "user_id": user_id,
                        "command": command_type,
                        "count": request_counters[user_id][command_type]
                    }
                )
                return
            
            request_counters[user_id][command_type] += 1
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator

# Заменить блок setup_logging() на:
def setup_logging():
    logger = logging.getLogger("main")
    logger.handlers.clear()
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Обработчик для errors.log
    error_handler = RotatingFileHandler(
        filename=ERRORS_LOG,
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # Обработчик для last.log
    last_log_handler = RotatingFileHandler(
        filename=LAST_LOG,
        maxBytes=5*1024*1024,
        backupCount=3,
        encoding='utf-8'
    )
    last_log_handler.setLevel(logging.INFO)
    last_log_handler.setFormatter(formatter)
    
    # Консольный вывод
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(error_handler)
    logger.addHandler(last_log_handler)
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)


# Логгирование (ваш оригинальный код)
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LAST_LOG),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("main")
error_handler = logging.FileHandler(ERRORS_LOG)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))


class ThrottledFilter(logging.Filter):
    last_log = 0
    
    def filter(self, record):
        if "200 OK" in record.getMessage():
            now = time.time()
            if now - self.last_log < 300:
                return False
            self.last_log = now
        return True

logger.addFilter(ThrottledFilter())

try:
    for lang in ["ru", "en", "tk"]:
        base_keys = set(TEXTS["ru"].keys())
        current_keys = set(TEXTS[lang].keys())
        missing = base_keys - current_keys
        if missing:
            logger.warning(f"Missing keys in {lang}: {missing}")
except Exception as e:
    logger.error(f"Localization check error: {str(e)}")

async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split('_')[1]
    user_id = query.from_user.id
    user_lang[user_id] = lang
    await query.edit_message_text(get_text(user_id, "lang_changed"))

def log_user(update: Update):
    uid = update.effective_user.id
    uname = update.effective_user.username or "N/A"
    entry = f"{uid} | {uname}\n"
    if not os.path.exists(USER_STATS_FILE) or entry not in open(USER_STATS_FILE).read():
        with open(USER_STATS_FILE, "a") as f:
            f.write(entry)

def log_admin_action(admin_id: int, action: str, details: dict = None):
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "admin_id": admin_id,
        "action": action,
        "details": details or {}
    }
    log_line = json.dumps(log_entry, ensure_ascii=False)
    
    with open(ADMIN_ACTIONS, "a") as f:
        f.write(log_line + "\n")
    
    logger.info(f"Admin Action: {log_line}")


async def send_admin_notification(context: ContextTypes.DEFAULT_TYPE, action: str, details: str, user_id: int):
    try:
        message = get_text(user_id, "admin_notification").format(
            action=action,
            time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            details=details
        )
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=message,
            parse_mode=None
        )
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления админу: {str(e)}")
        logger.error(traceback.format_exc())


def log_history(user_id, username, url):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(HISTORY_LOG, "a") as f:
            f.write(f"{timestamp} | {user_id} | {username} | {url}\n")
    except Exception as e:
        logger.error(f"History log error: {str(e)}")
        

async def send_zipped_logs(update: Update, context: ContextTypes.DEFAULT_TYPE, folder_name: str):
    try:
        user_id = update.effective_user.id
        password = os.getenv("ZIP_PASSWORD")
        if not password:
            await update.message.reply_text(get_text(user_id, "password_not_set"))
            return

        # Формируем абсолютные пути
        target_folder = {"logs": LOGS_DIR}.get(folder_name)

        if not target_folder:
            await update.message.reply_text(get_text(user_id, "invalid_folder_name"))
            return

        # Преобразование Path в строку
        zip_filename = str(BASE_DIR / f"logs.zip")

        # Проверка существования папки
        if not target_folder.exists():
            await update.message.reply_text(
                get_text(user_id, "folder_not_found").format(
                    folder_name=folder_name, 
                    target_folder=target_folder
                )
            )
            return

        file_list = []
        for root, _, files in os.walk(target_folder):
            file_list.extend([os.path.join(root, f) for f in files])
        
        if not file_list:
            await update.message.reply_text(
                get_text(user_id, "no_files_in_folder").format(folder_name=folder_name)
            )
            return

        total_files = len(file_list)
        progress_msg = await update.message.reply_text(
            get_text(user_id, "archive_start").format(total_files=total_files)
        )

        try:
            with pyzipper.AESZipFile(
                zip_filename,
                'w',
                encryption=pyzipper.WZ_AES
            ) as zipf:
                zipf.setpassword(password.encode())
                
                for i, file_path in enumerate(file_list, 1):
                    arcname = os.path.relpath(file_path, target_folder)
                    zipf.write(file_path, arcname, compress_type=pyzipper.ZIP_DEFLATED)
                    
                    if i % 5 == 0:
                        get_text(user_id, "archive_progress").format(
                            current=i,
                            total=total_files,
                            percent=int(i/total_files*100)
                        )

            with open(zip_filename, "rb") as zip_file:
                await update.message.reply_document(
                    document=InputFile(zip_file, filename=os.path.basename(zip_filename)))
            
            await progress_msg.delete()
        
        except Exception as e:
            logger.error(f"Ошибка при создании архива: {str(e)}", exc_info=True)
            await update.message.reply_text(get_text(user_id, "archive_failed"))
        
        finally:
            if os.path.exists(zip_filename):
                os.remove(zip_filename)

    except Exception as e:
        logger.error(f"Ошибка архивации: {str(e)}", exc_info=True)
        await update.message.reply_text(get_text(user_id, "archive_error")) 


def log_message(user_id, username, text):
    log_entry = f"[MSG] {datetime.datetime.now().isoformat()} | {user_id} | @{username}: {text}"
    print(f"\033[94m{log_entry}\033[0m")
    with open(MESSAGES_LOG, "a") as f:
        f.write(log_entry + "\n")

def is_admin(user_id):
    is_admin = user_id == ADMIN_ID
    logging.info(f"Проверка прав: user_id={user_id}, is_admin={is_admin}")
    return is_admin

def admin_required(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if not is_admin(user_id):
            await update.message.reply_text("Доступ только для администраторов!")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def too_fast(user_id):
    now = datetime.datetime.now().timestamp()
    if now - last_command_time[user_id] < 3:
        return True
    last_command_time[user_id] = now
    return False

def is_youtube_shorts(url: str) -> bool:
    return re.search(r"youtube\.com/shorts/", url) is not None


def parse_time(time_str: str) -> datetime.timedelta:
    unit = time_str[-1].lower()
    value = int(time_str[:-1])
    
    if unit == 'h':
        return datetime.timedelta(hours=value)
    elif unit == 'm':
        return datetime.timedelta(minutes=value)
    elif unit == 'd':
        return datetime.timedelta(days=value)
    else:
        raise ValueError("Invalid time unit")


def check_cookie_freshness():
    if not os.path.exists(INSTAGRAM_COOKIES):
        return False
    create_time = os.path.getctime(INSTAGRAM_COOKIES)
    return (time.time() - create_time) < COOKIE_AGE_LIMIT

async def on_shutdown(app):
    save_bans()
    logger.info("Данные сохранены в /user_states.txt")

def save_bans():
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Путь к файлу: {USER_STATES_FILE.absolute()}")

        data = []
        # Сохраняем баны в корректном формате
        for uid, info in banned_users.items():
            data.append(f"BAN:{uid}:{info['reason']}:{info['timestamp']}:{info['admin']}")
        
        # Атомарная запись
        with open(USER_STATES_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(data))
        
        logger.info(f"Данные сохранены: {len(data)} записей")
        
    except Exception as e:
        logger.error(f"Ошибка сохранения: {str(e)}", exc_info=True)

def load_bans():
    global banned_users
    try:
        if not USER_STATES_FILE.exists():
            logger.warning("Файл с банами не найден. Создан новый.")
            return

        with open(USER_STATES_FILE, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

        for line in lines:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.strip().split(':')
            if parts[0] == "BAN" and len(parts) == 5:
                uid = int(parts[1])
                banned_users[uid] = {
                    "reason": parts[2],
                    "timestamp": float(parts[3]),
                    "admin": int(parts[4])
                }
        
        logger.info(f"Загружено: {len(banned_users)} банов")
        
    except Exception as e:
        logger.error(f"Ошибка загрузки: {str(e)}", exc_info=True)

@rate_limit("download")
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text
    uname = update.effective_user.username or "N/A"
    log_message(uid, uname, text)

    # Проверка бана
    if uid in banned_users:
        try:
            ban_data = banned_users[uid]
            reason = ban_data.get("reason", get_text(uid, "no_reason"))
            await update.message.reply_text(
                get_text(uid, "banned_message").format(reason=reason)
            )
            log_admin_action(
                admin_id=0,  # Системное действие
                action="BANNED_ACCESS_ATTEMPT",
                details={
                    "user_id": uid,
                    "username": uname,
                    "message": text
                }
            )
            return
        except Exception as e:
            logger.error(f"Banned user handling error: {str(e)}")
            await update.message.reply_text(get_text(user.id, "access_restricted"))
            return

    if uid in banned_users or str(uid) in banned_users:
        actual_uid = uid if uid in banned_users else int(uid)

    # Проверка лимита очереди
    if len(user_queues[uid]) >= MAX_USER_QUEUE:
        await update.message.reply_text(
            get_text(uid, "queue_limit").format(
                count=MAX_USER_QUEUE,
                total=len(queue)
            )
        )
        return

    log_user(update)
    
    if re.match(r"^https?://", text):
        log_history(uid, uname, text)
        
        # Для YouTube предлагаем выбор формата
        if re.search(r"(youtube\.com|youtu\.be)", text):
            context.user_data['url'] = text
            keyboard = [
                [
                    InlineKeyboardButton("🎥 MP4", callback_data="format_video"),
                    InlineKeyboardButton("🎧 MP3", callback_data="format_mp3")
                ],
                [InlineKeyboardButton("📝 SRT", callback_data="format_txt")]
            ]
            await update.message.reply_text(
                get_text(uid, "select_format"),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            queue.append((update, context, text, 'auto'))
            user_queues[uid].append((update, context, text, 'auto'))
            await update.message.reply_text(get_text(uid, "added_to_queue"))
    else:
        await update.message.reply_text(get_text(uid, "send_link"))

    if not context.application.running:
        with open(PENDING_QUEUE_FILE, "a") as f:
            f.write(json.dumps({
                "user_id": uid,
                "url": text,
                "timestamp": datetime.datetime.now().isoformat()
            }) + "\n")
        return

async def post_init(app):
    background_tasks = []
    background_tasks.append(asyncio.create_task(download_worker()))
    background_tasks.append(asyncio.create_task(cleanup_task()))