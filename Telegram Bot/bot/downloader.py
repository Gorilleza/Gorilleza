import os, asyncio, time, logging
from yt_dlp import YoutubeDL
from telegram import (
    Update, InputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton )
from telegram.ext import ContextTypes
from bot.localization import get_text
from bot.utils import (
    save_bans, load_bans, queue, logger,
    user_queues )
from bot.config import (
    DOWNLOADS_DIR, MAX_FILE_SIZE,
    LOGS_DIR, INSTAGRAM_COOKIES,
    REQUEST_TIMEOUT, ADMIN_ACTIONS,
    USER_STATS_FILE, USER_STATES_FILE,
    FEEDBACK_LOG, REPORT_LOG, HISTORY_LOG,
    MESSAGES_LOG, ERRORS_LOG )

async def format_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    uid = query.from_user.id
    url = context.user_data.get('url')
    logger.info(f"Обработка кнопки: {data}, URL: {url}")
    if not url:
        logger.error("URL отсутствует в context.user_data")
        await query.edit_message_text(get_text(uid, "session_expired"))
        return
    try:
        context.user_data['url'] = url
        if data == "format_video":
            await query.edit_message_text(
                get_text(uid, "select_quality"),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("360p", callback_data="quality_360"),
                     InlineKeyboardButton("720p", callback_data="quality_720")],
                    [InlineKeyboardButton("1080p", callback_data="quality_1080"),
                     InlineKeyboardButton("MAX", callback_data="quality_best")]
                ])
            )
        elif data == "format_mp3":
            await process_mp3(query, context, url)
        elif data == "format_txt":
            await process_subtitles(query, context, url)
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}", exc_info=True)
        await query.edit_message_text(get_text(uid, "processing_error"))

async def process_mp3(query, context, url):
    uid = query.from_user.id
    try:
        logger.info(f"Начало обработки MP3 для {url}")
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'writethumbnail': True,
            'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s'),
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3')
            thumb = filename.replace('.mp3', '.webp')
        await query.edit_message_text(get_text(uid, "downloading"))
        await context.bot.send_audio(
            chat_id=uid,
            audio=open(filename, 'rb'),
            thumbnail=open(thumb, 'rb') if os.path.exists(thumb) else None,
            read_timeout=REQUEST_TIMEOUT,
            write_timeout=REQUEST_TIMEOUT
        )
        os.remove(filename)
        if os.path.exists(thumb):
            os.remove(thumb)
    except Exception as e:
        logger.error(f"Ошибка MP3: {str(e)}", exc_info=True)
        await query.edit_message_text(get_text(uid, 'download_error'))

async def process_subtitles(query, context, url):
    uid = query.from_user.id
    try:
        logger.info(f"Начало обработки субтитров для {url}")
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['ru', 'en'],
            'subtitlesformat': 'srt',
            'skip_download': True,
            'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s'),
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            subs = [f for f in os.listdir(DOWNLOADS_DIR)
                    if f.endswith('.srt') and info['title'] in f]
        if not subs:
            await query.edit_message_text(get_text(uid, "no_subtitles"))
            return
        await query.edit_message_text(get_text(uid, "downloading"))
        for sub_file in subs:
            FILE_PATH = os.path.join(DOWNLOADS_DIR, sub_file)
            try:
                await context.bot.send_document(
                    chat_id=uid,
                    document=open(FILE_PATH, 'rb'),
                    filename=sub_file,
                    read_timeout=REQUEST_TIMEOUT,
                    write_timeout=REQUEST_TIMEOUT
                )
            finally:
                if os.path.exists(FILE_PATH):
                    os.remove(FILE_PATH)
    except Exception as e:
        logger.error(f"Ошибка обработки субтитров: {str(e)}", exc_info=True)
        await query.edit_message_text(get_text(uid, "subtitle_error"))
        for f in os.listdir(DOWNLOADS_DIR):
            if f.endswith('.vtt'):
                try:
                    os.remove(os.path.join(DOWNLOADS_DIR, f))
                except:
                    pass

async def quality_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    uid = query.from_user.id
    url = context.user_data.get('url')
    logger.info(f"Выбор качества: {data} для {url}")
    if not url:
        logger.error("URL потерян")
        await query.edit_message_text(get_text(uid, "session_error"))
        return
    try:
        context.user_data['url'] = url
        queue.append((update, context, url, data))
        user_queues[uid].append((update, context, url, data))
        await query.edit_message_text(get_text(uid, "downloading"))
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        await query.edit_message_text("⚠ Ошибка обработки качества")

async def download_worker():
    quality_map = {
        "quality_360": "bestvideo[height<=360]+bestaudio/best[height<=360]",
        "quality_720": "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "quality_1080": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "quality_best": "bestvideo+bestaudio/best",
        "auto": "bestvideo+bestaudio/best"
    }

    while True:
        try:
            if not queue:
                await asyncio.sleep(2)
                continue

            update, context, url, quality = queue.popleft()
            user_id = update.effective_user.id
            
            if user_queues.get(user_id):
                user_queues[user_id].popleft()

            logger.info(f"Processing: {url} for user {user_id}")

            ydl_opts = {
                "format": quality_map.get(quality, "bestvideo+bestaudio/best"),
                "quiet": True,
                "no_warnings": True,
                "simulate": True,  # Не скачиваем, только получаем инфо
                "forceurl": True,
            }

            try:
                # Получаем метаданные без скачивания
                with YoutubeDL(ydl_opts) as ydl:
                    info = await asyncio.to_thread(ydl.extract_info, url, download=False)
                    
                    # Проверяем размер
                    if info.get('filesize_approx') or info.get('filesize'):
                        file_size = info.get('filesize') or info.get('filesize_approx')
                        
                        if file_size > MAX_FILE_SIZE:
                            await context.bot.send_message(
                                chat_id=user_id,
                                text=get_text(user_id, "file_too_large_pre_download")
                            )
                            logger.warning(
                                f"Rejected large file pre-download: {url} "
                                f"Size: {file_size/1024/1024:.2f}MB"
                            )
                            continue

                # Если проверка пройдена - скачиваем
                ydl_opts.update({
                    "outtmpl": os.path.join(DOWNLOADS_DIR, "%(title)s.%(ext)s"),
                    "merge_output_format": "mp4",
                    "postprocessors": [
                        {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"},
                        {"key": "FFmpegMetadata"}
                    ],
                    "simulate": False  # Реальное скачивание
                })

                with YoutubeDL(ydl_opts) as ydl:
                    info = await asyncio.to_thread(ydl.extract_info, url, download=True)
                    filename = ydl.prepare_filename(info)
                    
                    if not filename.endswith(".mp4"):
                        new_filename = os.path.splitext(filename)[0] + ".mp4"
                        os.rename(filename, new_filename)
                        filename = new_filename

                # Проверка размера файла
                file_size = os.path.getsize(filename)
                
                if file_size > MAX_FILE_SIZE:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=get_text(user_id, "file_too_large")
                    )
                    
                    if os.path.exists(filename):
                        try:
                            os.remove(filename)
                            logger.warning(f"Removed oversized file: {filename}")
                        except Exception as remove_error:
                            logger.error(f"Failed to remove {filename}: {str(remove_error)}")
                            log_admin_action(
                                admin_id=ADMIN_ID,
                                action="FILE_REMOVE_ERROR",
                                details={
                                    "filename": filename,
                                    "error": str(remove_error),
                                    "user_id": user_id
                                }
                            )
                    
                    # Очистка временных файлов
                    temp_files = [
                        f"{filename}.part",
                        f"{os.path.splitext(filename)[0]}.webp",
                        f"{os.path.splitext(filename)[0]}.jpg"
                    ]
                    
                    for temp_file in temp_files:
                        if os.path.exists(temp_file):
                            try:
                                os.remove(temp_file)
                                logger.info(f"Cleaned temp file: {temp_file}")
                            except Exception as temp_error:
                                logger.error(f"Temp cleanup failed: {temp_file} - {str(temp_error)}")
                    
                    logger.warning(
                        f"File size limit exceeded - User: {user_id}, "
                        f"Size: {file_size/1024/1024:.2f}MB, "
                        f"Limit: {MAX_FILE_SIZE/1024/1024}MB"
                    )
                    
                    continue

                # Отправка файла если проверка пройдена
                await context.bot.send_chat_action(user_id, "upload_video")
                with open(filename, "rb") as video_file:
                    await context.bot.send_video(
                        chat_id=user_id,
                        video=InputFile(video_file),
                        filename=os.path.basename(filename),
                        read_timeout=REQUEST_TIMEOUT,
                        write_timeout=REQUEST_TIMEOUT,
                        supports_streaming=True
                    )
                logger.info(f"Successfully sent video to {user_id}")

            except Exception as download_error:
                logger.error(f"Download failed: {str(download_error)}")
                await context.bot.send_message(
                    user_id,
                    get_text(user_id, "download_error") + f"\nError: {str(download_error)}"
                )

            finally:
                if os.path.exists(filename):
                    try:
                        os.remove(filename)
                        logger.info(f"Cleaned main file: {filename}")
                    except Exception as final_error:
                        logger.error(f"Final cleanup error: {str(final_error)}")
                
                for f in os.listdir(DOWNLOADS_DIR):
                    if f.startswith("tmp") or f.endswith(".part"):
                        try:
                            os.remove(os.path.join(DOWNLOADS_DIR, f))
                        except Exception as temp_error:
                            logger.error(f"Temp file cleanup error: {str(temp_error)}")

        except Exception as error:
                logger.error(f"Download error: {str(error)}")
                await context.bot.send_message(
                    user_id,
                    get_text(user_id, "download_error")
                )

        except Exception as worker_error:
            logger.critical(f"Worker error: {str(worker_error)}")
            await asyncio.sleep(5)

        await asyncio.sleep(1)

async def cleanup_task():
    while True:
        for f in os.listdir(DOWNLOADS_DIR):
            path = os.path.join(DOWNLOADS_DIR, f)
            if os.path.isfile(path):  # Проверка, что это файл
                if os.stat(path).st_mtime < (time.time() - 3600):
                    try:
                        os.remove(path)
                    except Exception as e:
                        logger.error(f"Ошибка удаления: {str(e)}")
        await asyncio.sleep(3600)

