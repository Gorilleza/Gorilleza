from bot.config import user_lang

TEXTS = {
    "ru": {
        "start": "🎬 Привет! Просто отправь мне ссылку на видео. Загружаются видео не больше 50МБ",
        "help": ("📖 Доступные команды:\n"
                "/start - начать\n"
                "/help - помощь\n"
                "/lang - выбрать язык\n"
                "/feedback - оставить отзыв\n"
                "/report - сообщить об ошибке\n"
                "/queue - статус очереди\n"
                "/status - статус сервисов\n"),
        "lang_select": "🌍 Выберите язык:",
        "lang_changed": "✅ Язык изменен: РУССКИЙ",
        "added_to_queue": "⏳ Видео добавлено в очередь!",
        "send_link": "❌ Это не ссылка. Отправь мне URL видео.",
        "banned_alert": "🚫 Забаненный пользователь пытался получить доступ",
        "admin_help": ("⚙ Админ-команды:\n"
                "/admin users - список пользователей\n"
                "/admin stats - статистика\n"
                "/admin ban [ID] <причина> - заблокировать\n"
                "/admin unban [ID] - разблокировать\n"
                "/admin logs - все логи\n"
                "/admin broadcast [msg] - рассылка\n"
                "/admin offbot - выключить бота\n"),
        "service_status": "📡 Статус сервисов:\n"
                "YouTube: {yt}\n"
                "YouTube Shorts: {yt_shorts}\n"
                "TikTok: {tt}\n"
                "Instagram: {ig}",
        "invalid_admin_cmd": "⚠ Некорректная команда админа",
        "user_banned": "🔨 Пользователь {user_id} заблокирован",
        "user_unbanned": "🔓 Пользователь {user_id} разблокирован",
        "specify_id": "⚠ Укажите ID пользователя",
        "select_format": "🎚 Выберите формат:",
        "select_quality": "🖼 Выберите качество видео:",
        "downloading": "⏳ Начинаю загрузку...",
        "no_subtitles": "❌ Субтитры не найдены",
        "mp3_title": "🎵 {title} [{channel}]",
        "download_error": "❌ Ошибка при загрузке",
        "subtitle_error": "❌ Ошибка загрузки субтитров",
        "uploading": "📤 Идет отправка файла...",
        "server_error": "🔧 Ошибка обработки на стороне сервера",
        "broadcast_usage": "✉ Использование: /broadcast <сообщение>",
        "broadcast_start": "🚀 Рассылка начата. Пользователей: {}",
        "broadcast_progress": "📤 Отправлено: {}/{}",
        "broadcast_complete": "✅ Рассылка завершена. Успешно: {}, Неудачно: {}",
        "banned_message": "🚫 Вы заблокированы. Причина: {reason}",
        "queue_status": "📊 Ваши задачи в очереди: {count}\nВсего задач: {total}",
        "file_too_large": "⚠️ Файл больше 50 МБ. Используйте @Gozilla_bot",
        "feedback_sent": "📨 Ваш отзыв сохранён",
        "report_sent": "⚠️ Сообщение об ошибке отправлено",
        "myhistory_header": "📝 Последние загрузки:\n",
        "no_history": "📭 История загрузок отсутствует",
        "invalid_time": "⚠ Некорректный формат времени (используйте 1h, 30m)",
        "admin_log_notification": "🛡 Действие администратора: {action}\n🔗 Детали: {details}",
        "access_denied": "Доступ запрещен",
        "critical_error": "Критическая ошибка системы",
        "invalid_user": "❌ Неверный ID пользователя",
        "no_reason": "Причина не указана",
        "session_error": "❌ Ошибка сессии",
        "session_expired": "❌ Ошибка: сессия устарела",
        "temp_access_denied": "🔇 Доступ временно ограничен",
        "access_restricted": "🚫 Доступ ограничен",
        "processing_error": "🚨 Ошибка обработки запроса",
        "system_restriction": "⛔ Системное ограничение",
        "invalid_session": "🔒 Недействительная сессия",
        "folder_not_found": "❌ Папка {folder_name} не найдена по пути: {target_folder}",
        "no_files_in_folder": "⚠️ В папке {folder_name} нет файлов",
        "archive_start": "⏳ Начало архивации ({total_files} файлов)...",
        "archive_progress": "📦 Архивировано {current}/{total} файлов ({percent}%)",
        "archive_failed": "🔥 Критическая ошибка при создании архива",
        "archive_error": "❌ Не удалось обработать запрос. Проверьте логи.",
        "feedback_format_error": "⚠️ Неверный формат. Введите: /feedback [ваш отзыв]",
        "admin_notification": "🛎️ Уведомление системы\n📌 Действие: {action}\n📅 Время: {time}\n🔍 Детали:\n{details}",
        "report_format_error": "⚠️ Неверный формат. Введите: /report [описание проблемы]",
        "rate_limit": "⚠️ Слишком много запросов. Попробуйте позже.",
        "auth_error": "🔑 Ошибка авторизации. Администратор уведомлен.",
        "cookie_expired": "⚠️ Куки Instagram устарели! Обновите их.",
        "queue_limit": "⚠️ {count}/{total} задач в очереди",
        "access_restricted": "🚫 Доступ ограничен",
        "temp_access_denied": "🔇 Доступ временно ограничен",
        "service_status_header": "🔄 Актуальный статус (проверено в реальном времени):\n{status_text}",
        "access_denied": "🚫 Доступ запрещен",
        "shutdown": "🛑 Выключение бота...",
        "server_error": "🔥 Ошибка сервера",
        "critical_error": "💥 Критическая ошибка системы",
        "broadcast_no_users": "❌ Нет пользователей для рассылки",
        "stats_message": "👥 Пользователей: {users}\n📥 Загрузок: {history}\n📊 Очередь: {queue}",
        "queue_limit": "⚠️ {count}/{total} задач в очереди",
        "access_restricted": "🚫 Доступ ограничен",
        "temp_access_denied": "🔇 Доступ временно ограничен",
        "admin_notification": (
            "🛎️ Уведомление системы\n"
            "📌 Действие: {action}\n"
            "📅 Время: {time}\n"
            "🔍 Детали:\n{details}"),
        "shutdown": "🛑 Выключение бота...",
        "broadcast_read_error": "❌ Ошибка чтения данных пользователей",
        "broadcast_no_valid": "❌ Нет валидных пользователей",
        "server_error": "🔥 Ошибка сервера",
        "new_feedback": "📣 Новый фидбек!\n👤 Пользователь: @{username} (ID: {user_id})\n💬 Содержание: {text}",
        "new_report": "⚠️ Новый репорт!\n👤 Пользователь: @{username} (ID: {user_id})\n💬 Содержание: {text}",
        "access_denied": "🚫 Доступ запрещен",
        "broadcast_usage": "✉ Использование: /admin broadcast <сообщение>",
        "broadcast_start": "🚀 Рассылка начата. Пользователей: {}",
        "broadcast_progress": "📤 Отправлено: {}/{}",
        "broadcast_complete": "✅ Рассылка завершена. Успешно: {}, Неудачно: {}",
        "broadcast_no_users": "❌ Нет пользователей для рассылки",
        "broadcast_read_error": "❌ Ошибка чтения данных пользователей",
        "broadcast_no_valid": "❌ Нет валидных пользователей",
        "rate_limit": "⚠️ Слишком много запросов. Попробуйте через {timeout} сек. (Rate limit)",

        "user_unbanned_notify": "🔓 Ваш доступ восстановлен",
        "file_too_large_pre_download": "⚠️ Файл превышает 50 МБ\nСкачивание невозможно"
        
    },
    "en": {
        "start": "🎬 Hi! Just send me a video link. Downloading only less than 50MB",
        "help": ("📖 Available commands:\n"
                "/start - begin\n"
                "/help - help\n"
                "/lang - change language\n"
                "/feedback - send feedback\n"
                "/report - report issue\n"
                "/queue - queue status\n"
                "/status - check services\n"),
        "lang_select": "🌍 Choose language:",
        "lang_changed": "✅ Language changed: ENGLISH",
        "added_to_queue": "⏳ Video added to queue!",
        "send_link": "❌ Not a valid link. Please send a video URL.",
        "banned_alert": "🚫 Banned user tried to access",
        "admin_help": ("⚙ Admin commands:\n"
                "/admin users - user list\n"
                "/admin stats - statistics\n"
                "/admin ban [ID] <reason> - ban user\n"
                "/admin unban [ID] - unban user\n"
                "/admin logs - all logs\n"
                "/admin broadcast [msg] - broadcast\n"
                "/admin offbot - off bot\n"),
        "service_status": "📡 Service status:\n"
                "YouTube: {yt}\n"
                "YouTube Shorts: {yt_shorts}\n"
                "TikTok: {tt}\n"
                "Instagram: {ig}",
        "user_banned": "🔨 User {user_id} banned",
        "user_unbanned": "🔓 User {user_id} unbanned",
        "specify_id": "⚠ Specify user ID",
        "select_format": "🎚 Select format:",
        "select_quality": "🖼 Select video quality:",
        "downloading": "⏳ Starting download...",
        "no_subtitles": "❌ Subtitles not found",
        "mp3_title": "🎵 {title} [{channel}]",
        "download_error": "❌ Download error",
        "subtitle_error": "❌ Subtitle download error",
        "uploading": "📤 Uploading file...",
        "server_error": "🔧 Server-side processing error",
        "broadcast_usage": "✉ Usage: /broadcast <message>",
        "broadcast_start": "🚀 Broadcast started. Users: {}",
        "broadcast_progress": "📤 Sent: {}/{}",
        "broadcast_complete": "✅ Broadcast complete. Success: {}, Failed: {}",
        "banned_message": "🚫 You are banned. Reason: {reason}",
        "queue_status": "📊 Your queued tasks: {count}\nTotal tasks: {total}",
        "file_too_large": "⚠️ Files over 50MB not supported. Use @Gozilla_bot",
        "feedback_sent": "📨 Feedback saved",
        "report_sent": "⚠️ Error report sent",
        "service_status": "📡 Service status:\nYouTube: {yt}\nTikTok: {tt}\nInstagram: {ig}",
        "myhistory_header": "📝 Recent downloads:\n",
        "no_history": "📭 No download history",
        "invalid_time": "⚠ Invalid time format (use 1h, 30m)",
        "admin_log_notification": "🛡 Admin Action: {action}\n🔗 Details: {details}",
        "access_denied": "Access denied",
        "critical_error": "Critical system error",
        "invalid_user": "❌ Invalid user ID",
        "no_reason": "No reason specified",
        "invalid_admin_cmd": "⚠ Invalid admin command",
        "Ошибка при загрузке": "Download error",
        "session_error": "❌ Session error",
        "session_expired": "❌ Error: session expired",
        "temp_access_denied": "🔇 Access temporarily restricted",
        "access_restricted": "🚫 Access restricted",
        "processing_error": "🚨 Request processing error",
        "system_restriction": "⛔ System restriction",
        "invalid_session": "🔒 Invalid session",
        "cookie_expired": "⚠️ Instagram cookies expired! Renew them.",
        "queue_limit": "⚠️ {count}/{total} tasks in queue",
        "access_restricted": "🚫 Access restricted",
        "temp_access_denied": "🔇 Temporarily restricted",
        "folder_not_found": "❌ Folder {folder_name} not found at path: {target_folder}",
        "no_files_in_folder": "⚠️ No files in {folder_name} folder",
        "archive_start": "⏳ Starting archive creation ({total_files} files)...",
        "archive_progress": "📦 Archived {current}/{total} files ({percent}%)",
        "archive_failed": "🔥 Critical error creating archive",
        "archive_error": "❌ Failed to process request. Check logs.",
        "feedback_format_error": "⚠️ Invalid format. Use: /feedback [your feedback]",
        "admin_notification": "🛎️ System notification\n📌 Action: {action}\n📅 Time: {time}\n🔍 Details:\n{details}",
        "report_format_error": "⚠️ Invalid format. Use: /report [issue description]",
        "rate_limit": "⚠️ Too many requests. Try again later.",
        "auth_error": "🔑 Authorization error. Admin notified.",
        "service_status_header": "🔄 Current status (real-time check):\n{status_text}",
        "access_denied": "🚫 Access denied",
        "shutdown": "🛑 Shutting down bot...",
        "server_error": "🔥 Server error",
        "critical_error": "💥 Critical system error",
        "broadcast_no_users": "❌ No users for broadcast",
        "stats_message": "👥 Users: {users}\n📥 Downloads: {history}\n📊 Queue: {queue}",
        "queue_limit": "⚠️ {count}/{total} tasks in queue",
        "access_restricted": "🚫 Access restricted", 
        "temp_access_denied": "🔇 Temporarily restricted",
        "admin_notification": (
            "🛎️ System notification\n"
            "📌 Action: {action}\n"
            "📅 Time: {time}\n"
            "🔍 Details:\n{details}"),
        "shutdown": "🛑 Shutting down bot...",
        "broadcast_read_error": "❌ Error reading users data",
        "broadcast_no_valid": "❌ No valid users found",
        "server_error": "🔥 Server error",
        "new_feedback": "📣 New feedback!\n👤 User: @{username} (ID: {user_id})\n💬 Content: {text}",
        "new_report": "⚠️ New Report!\n👤 User: @{username} (ID: {user_id})\n💬 Content: {text}",
        "access_denied": "🚫 Access denied",
        "broadcast_usage": "✉ Usage: /admin broadcast <message>",
        "broadcast_start": "🚀 Broadcast started. Users: {}",
        "broadcast_progress": "📤 Sent: {}/{}",
        "broadcast_complete": "✅ Broadcast complete. Success: {}, Failed: {}",
        "broadcast_no_users": "❌ No users for broadcast",
        "broadcast_read_error": "❌ Error reading users data",
        "broadcast_no_valid": "❌ No valid users found",
        "user_unbanned_notify": "🔓 Your access has been unlocked",
        "rate_limit": "⚠️ Too many requests. Try again in {timeout} sec. (Rate limit)",
    },
    "tk": {
        "start": "🎬 Salam! Diňe wideo salgysyny iberiň. 50MB-dan uly däl wideolar ýüklener",
        "help": (
            "📖 Elýeterli buýruklar:\n"
            "/start - başla\n"
            "/help - kömek\n"
            "/lang - dil saýla\n"
            "/feedback - pikir ýaz\n"
            "/report - ýalňyşlyk barada habar ber\n"
            "/queue - nobat ýagdaýy\n"
            "/status - serişdeleriň ýagdaýy\n"
            "/myhistory - ýükleme taryhym"
        ),
        "lang_select": "🌍 Dil saýlaň:",
        "lang_changed": "✅ Dil üýtgedildi: TÜRKMEN",
        "added_to_queue": "⏳ Wideo nobata goşuldy!",
        "send_link": "❌ Dogry salgy däl. Wideo salgysyny iberiň.",
        "banned_alert": "🚫 Bloklanan ulanyjy girmäge synanyşdy",
        "admin_help": (
            "⚙ Admin buýruklary:\n"
            "/admin users - ulanyjylaryň sanawy\n"
            "/admin stats - statistika\n"
            "/admin ban [ID] <sebäp> - ulanyjyny blokla\n"
            "/admin unban [ID] - blokdan aýyr\n"
            "/admin logs - ähli loglar\n"
            "/admin broadcast [habar] - habar iber"
            "/admin offbot - bot uçürmek\n"
        ),
        # Добавленные/исправленные ключи
        "service_status": (
            "📡 Serişdeleriň ýagdaýy:\n"
            "YouTube: {yt}\n"
            "YouTube Shorts: {yt_shorts}\n"
            "TikTok: {tt}\n"
            "Instagram: {ig}"
        ),
        "user_banned": "🔨 Ulanyjy {user_id} bloklandy",
        "user_unbanned": "🔓 Ulanyjy {user_id} blokdan aýryldy",
        "specify_id": "⚠ Ulanyjy ID-syny görkeziň",
        "select_format": "🎚 Format saýlaň:",
        "select_quality": "🖼 Wideonyň hilini saýlaň:",
        "downloading": "⏳ Ýüklemek başlandy...",
        "no_subtitles": "❌ Subtitrler tapylmady",
        "mp3_title": "🎵 {title} [{channel}]",
        "download_error": "Ýükleme ýalňyşlygy",
        "subtitle_error": "❌ Subtitr ýükleme ýalňyşlygy",
        "uploading": "📤 Faýl iberilýär...",
        "server_error": "🔧 Serwer tarapynda ýalňyşlyk",
        "broadcast_usage": "✉ Ulanylyş: /broadcast <habar>",
        "broadcast_start": "🚀 Habar iberildi. Ulanyjylar: {}",
        "broadcast_progress": "📤 Iberildi: {}/{}",
        "broadcast_complete": "✅ Habar tamamlandy. Üstünlik: {}, Şowsuz: {}",
        "banned_message": "🚫 Siz bloklandyňyz. Sebäbi: {reason}",
        "queue_status": "📊 Nobatyňyzda: {count}\nJemi: {total}",
        "file_too_large": "⚠️ 50MB-dan uly faýllar goldanylmaýar. @Gozilla_bot ulanyň",
        "feedback_sent": "📨 Pikiriňiz ýatda saklandy",
        "report_sent": "⚠️ Ýalňyşlyk barada habar iberildi",
        "myhistory_header": "📝 Soňky ýüklemeler:\n",
        "no_history": "📭 Ýükleme taryhy ýok",
        "invalid_time": "⚠ Nädogry wagt formaty (1h, 30m ýaly ulanyň)",
        "access_denied": "🚫 Girizilmek ýadakyldy",
        "critical_error": "💥 Kritisistem ýalňyşlygy",
        "admin_log_notification": "🛡 Admin hereketi: {action}\n🔗 Jikme-jiklikler: {details}",
        "Ошибка при загрузке": "Ýükleme ýalňyşlygy",
        "invalid_admin_cmd": "⚠ Nädogry admin buýrugy",
        "invalid_user": "❌ Nädogry ulanyjy ID",
        "no_reason": "Sebäp görkezilmedi",
        "session_error": "❌ Sessiýa ýalňyşlygy",
        "session_expired": "❌ Ýalňyşlyk: sessiýa möhleti gutardy",
        "temp_access_denied": "🔇 Wagtyň çäkli girizilmegi",
        "access_restricted": "🚫 Girizilmek çäklendi",
        "processing_error": "🚨 Sorag işleme ýalňyşlygy",
        "system_restriction": "⛔ Ulgam çägi",
        "invalid_session": "🔒 Nädogry sessiýa",
        "cookie_expired": "⚠️ Instagram çörekleri möhleti gutardy! Täzeleň.",
        "queue_limit": "⚠️ Nöbetde {count}/{total} iş",
        "access_restricted": "🚫 Girizilmek çäklendi",
        "temp_access_denied": "🔇 Wagtyň çäkli girizilmegi",
        "folder_not_found": "❌ {folder_name} papkasynyň ýoly tapylmady: {target_folder}",
        "no_files_in_folder": "⚠️ {folder_name} papkasynda faýl ýok",
        "archive_start": "⏳ Arhiw döredilýär ({total_files} faýl)...",
        "archive_progress": "📦 Arhiwlenen {current}/{total} faýl ({percent}%)",
        "archive_failed": "🔥 Arhiw döretmekde kritis ýalňyşlyk",
        "archive_error": "❌ Sorap işlenmedi. Loglary barlaň.",
        "feedback_format_error": "⚠Ýalňyş format. /feedback [pikiriňiz] ýaly ulanyň",
        "admin_notification": "🛎️ Ulgam habarnamasy\n📌 Hereket: {action}\n📅 Wagt: {time}\n🔍 Jikme-jiklikler:\n{details}",
        "report_format_error": "⚠Ýalňyş format. /report [mesele düşündirişi] ýaly ulanyň",
        "rate_limit": "⚠️ Gaty köp sorag. Soňra synanyşyň.",
        "auth_error": "🔑 Ygtyýarnama ýalňyşlygy. Admin habarlandyryldy.",
        "service_status_header": "🔄 Häzirki ýagdaý (realtime barlag):\n{status_text}",
        "access_denied": "🚫 Girizilmek ýadakyldy",
        "shutdown": "🛑 Bot öçürilýär...",
        "server_error": "🔥 Serwer ýalňyşlygy",
        "critical_error": "💥 Kritisistem ýalňyşlygy",
        "broadcast_no_users": "❌ Habar ibermek üçin ulanyjy ýok",
        "stats_message": "👥 Ulanyjylar: {users}\n📥 Ýüklemeler: {history}\n📊 Nöbet: {queue}",
        "queue_limit": "⚠️ Nöbetde {count}/{total} iş",
        "access_restricted": "🚫 Girizilmek çäklendi",
        "temp_access_denied": "🔇 Wagtyň çäkli girizilmegi",
        "admin_notification": (
            "🛎️ Ulgam habarnamasy\n"
            "📌 Hereket: {action}\n"
            "📅 Wagt: {time}\n"
            "🔍 Jikme-jiklikler:\n{details}"),
        "shutdown": "🛑 Bot öçürilýär...",
        "broadcast_read_error": "❌ Ulanyjy maglumatlary okalýarka ýalňyşlyk",
        "broadcast_no_valid": "❌ Dogry ulanyjy tapylmady",
        "server_error": "🔥 Serwer ýalňyşlygy",
        "new_feedback": "📣 Täze pikiriňiz!\n👤 Ulanyjy: @{username} (ID: {user_id})\n💬 Mazmuny: {text}",
        "new_report": "⚠️ Täze hasabat!\n👤 Ulanyjy: @{username} (ID: {user_id})\n💬 Mazmuny: {text}",
        "access_denied": "🚫 Girizilmek ýadakyldy",
        "broadcast_usage": "✉ Ulanylyş: /admin broadcast <habar>",
        "broadcast_start": "🚀 Habar iberildi. Ulanyjylar: {}",
        "broadcast_progress": "📤 Iberildi: {}/{}",
        "broadcast_complete": "✅ Habar tamamlandy. Üstünlik: {}, Şowsuz: {}",
        "broadcast_no_users": "❌ Habar ibermek üçin ulanyjy ýok",
        "broadcast_read_error": "❌ Ulanyjy maglumatlary okalýarka ýalňyşlyk",
        "broadcast_no_valid": "❌ Dogry ulanyjy tapylmady",
        "user_unbanned_notify": "🔓 Your access has been unlocked",
        "rate_limit": "⚠️ Gaty köp sorag. {timeout} sek. soňra synanyşyň (Rate limit)",
    }
}


def get_text(user_id: int, key: str) -> str:
    lang = user_lang.get(user_id, "ru")
    text = TEXTS.get(lang, {}).get(key)
    
    if not text:
        text = TEXTS["ru"].get(key, f"[{key}] Translation missing")
    
    return text

