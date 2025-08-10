import os, datetime, asyncio, signal, traceback
from io import BytesIO
from telegram import Update
from telegram.ext import ContextTypes
from bot.localization import get_text
from pathlib import Path
from bot.utils import (
    log_admin_action, send_zipped_logs,
    is_admin, save_bans, LOGS_DIR,
    banned_users, user_lang, 
    logger, queue )
from bot.config import (
    INSTAGRAM_COOKIES, ADMIN_ID, ADMIN_ACTIONS,
    LOGS_DIR, USER_STATS_FILE, USER_STATES_FILE,
    FEEDBACK_LOG, REPORT_LOG, HISTORY_LOG,
    MESSAGES_LOG, ERRORS_LOG )


async def handle_admin_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /admin logs"""
    await admin_wrapper(update, context, _logs_handler)

async def _logs_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Логика обработки логов"""
    user_id = update.effective_user.id
    await send_zipped_logs(update, context, "logs")
    log_admin_action(user_id, "LOGS_DOWNLOAD")

async def handle_2fa_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_code = update.message.text
    totp = pyotp.TOTP(TOTP_SECRET)
    
    # Проверка кода и резервных кодов
    if (totp.verify(user_code, valid_window=TOTP_WINDOW) 
        or user_code in TOTP_BACKUP_CODES):
        
        # Обновление сессии
        context.user_data['admin_session'] = datetime.now()
        await update.message.reply_text("✅ Сессия активна 5 минут")
        
        # Повторный вызов команды
        return await handle_admin_command(update, context)
    
    await update.message.reply_text("❌ Неверный код. Попробуйте снова.")
    return 1  # Остаемся в состоянии 2FA

async def admin_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, command_handler):
    """Обертка для административных команд"""
    user = update.effective_user
    
    # Проверка базовых прав
    if not is_admin(user.id):
        await update.message.reply_text(get_text(user.id, "access_denied"))
        return

async def admin_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка прав и инициализация админ-сессии"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 Команда доступна только администраторам")
        return ConversationHandler.END
    
    await update.message.reply_text("🔒 Введите код аутентификации:")
    return ADMIN_AWAIT_CODE

async def handle_admin_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кода аутентификации для администраторов"""
    if verify_2fa_code(update.message.text):
        await execute_admin_command(update, context)
    else:
        await update.message.reply_text("❌ Неверный код. Попробуйте снова:")
        return ADMIN_AWAIT_CODE  # Остаёмся в состоянии аутентификации
    
    context.user_data.clear()
    return ConversationHandler.END

def setup_handlers():
    # Обработчики для обычных пользователей
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & ~filters.User(ADMIN_ID),
        handle_message
    ))

    # Отдельный ConversationHandler для административных команд
    admin_handler = ConversationHandler(
        entry_points=[
            CommandHandler("admin", admin_command_wrapper),
            CommandHandler("ban", admin_command_wrapper),
            CommandHandler("logs", admin_command_wrapper)
            
        ],
        states={
            ADMIN_AWAIT_CODE: [
                MessageHandler(filters.TEXT, handle_admin_auth)
            ]
        },
        fallbacks=[CommandHandler("cancel", lambda u,c: ConversationHandler.END)],
        allow_reentry=True
    )
    app.add_handler(admin_handler)

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if os.path.exists(USER_STATS_FILE):
        await update.message.reply_document(document=open(USER_STATS_FILE, "rb"))

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    users = sum(1 for _ in open(USER_STATS_FILE)) if os.path.exists(USER_STATS_FILE) else 0
    history = sum(1 for _ in open(HISTORY_LOG)) if os.path.exists(HISTORY_LOG) else 0
    await update.message.reply_text(
        get_text(update.effective_user.id, "stats_message").format(
            users=users,
            history=history,
            queue=len(queue)
        )
    )

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён.")
        return
    await admin_wrapper(update, context, _ban_handler)
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /admin ban <user_id> <reason>")
        return
    user_id = int(args[0])
    reason = ' '.join(args[1:])
    banned_users[user_id] = (reason, datetime.datetime.now().timestamp())
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=get_text(user_id, "banned_message").format(reason=reason)
        )
    except Exception as e:
        logger.error(f"Can't send ban message to {user_id}: {e}")
    log_admin_action(update.effective_user.id, f"Banned {user_id} for {reason}")
    await update.message.reply_text(f"User {user_id} banned")

async def handle_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        args = context.args
        lang = user_lang[user.id]

        if len(args) < 2:
            await update.message.reply_text(get_text(user.id, "specify_id"))
            log_admin_action(
                admin_id=user.id,
                action="BAN_FAILED",
                details={"reason": "Missing arguments"}
            )
            return

        target_user_id_str = args[1]
        reason = ' '.join(args[2:]) or get_text(user.id, "no_reason")

        try:
            target_user_id = int(target_user_id_str)
        except ValueError:
            await update.message.reply_text(get_text(user.id, "invalid_user"))
            log_admin_action(
                admin_id=user.id,
                action="BAN_FAILED",
                details={"error": f"Invalid user_id: {target_user_id_str}"}
            )
            return

        try:
            chat_member = await context.bot.get_chat_member(target_user_id, target_user_id)
            username = chat_member.user.username or "N/A"
        except Exception as e:
            await update.message.reply_text(get_text(user.id, "invalid_user"))
            log_admin_action(
                admin_id=user.id,
                action="BAN_FAILED",
                details={
                    "target_user": target_user_id,
                    "error": str(e)
                }
            )
            return
            
        banned_users[target_user_id] = {
            "reason": reason,
            "timestamp": datetime.datetime.now().timestamp(),
            "admin": user.id
        }
        save_bans()

        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=get_text(target_user_id, "banned_message").format(reason=reason)
            )
        except Exception as e:
            logger.error(f"Can't send ban message to {target_user_id}: {e}")

        log_admin_action(
            admin_id=user.id,
            action="USER_BAN",
            details={
                "target_user": target_user_id,
                "username": username,
                "reason": reason,
                "duration": "permanent"
            }
        )

        await update.message.reply_text(
            get_text(user.id, "user_banned").format(user_id=target_user_id)
        )

    except Exception as e:
        logger.error(f"Ban error: {str(e)}", exc_info=True)
        log_admin_action(
            admin_id=user.id,
            action="BAN_ERROR",
            details={
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            
        )
        logger.error(f"CRITICAL BAN ERROR: {str(e)}")
        await update.message.reply_text("🔨 " + get_text(user.id, "server_error"))

    Path(USER_STATES_FILE).touch(exist_ok=True)
    save_bans()
        
async def handle_unban(update: Update, context: ContextTypes.DEFAULT_TYPE, args: list):
    try:
        user = update.effective_user
        
        # Проверка прав администратора
        if not is_admin(user.id):
            await update.message.reply_text(get_text(user.id, "access_denied"))
            return

        # Проверка наличия аргументов
        if len(args) < 1:
            await update.message.reply_text(get_text(user.id, "specify_id"))
            log_admin_action(
                admin_id=user.id,
                action="UNBAN_FAILED",
                details={"reason": "Missing user ID"}
            )
            return

        # Извлекаем ID пользователя из аргументов
        target_user_id_str = args[0]  # args уже не содержит подкоманду "unban"
        try:
            target_user_id = int(target_user_id_str)
        except ValueError:
            await update.message.reply_text(get_text(user.id, "invalid_user"))
            log_admin_action(
                admin_id=user.id,
                action="UNBAN_FAILED",
                details={"error": f"Invalid user ID: {target_user_id_str}"}
            )
            return

        # Проверка существования бана
        if target_user_id not in banned_users:
            await update.message.reply_text(
                get_text(user.id, "user_unbanned").format(user_id=target_user_id) + " (не был забанен)"
            )
            return

        # Снятие бана и сохранение
        del banned_users[target_user_id]
        save_bans()

        await update.message.reply_text(
            get_text(user.id, "user_unbanned").format(user_id=target_user_id)
        )

        log_admin_action(
            admin_id=user.id,
            action="USER_UNBAN",
            details={"target_user": target_user_id}
        )

        await context.bot.send_message(
            chat_id=target_user_id,
            text=get_text(target_user_id, "user_unbanned_notify")
        )

    except Exception as e:
        logger.error(f"Unban error: {str(e)}", exc_info=True)
        logger.error(f"Can't send unban message: {e}")
        await update.message.reply_text(get_text(user.id, "server_error"))
        log_admin_action(
            admin_id=user.id,
            action="UNBAN_ERROR",
            details={"error": str(e)}
        )

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE, args: list):
    if not is_admin(update.effective_user.id): 
        return
    
    if not args:
        await update.message.reply_text(get_text(update.effective_user.id, "broadcast_usage"))
        return
    
    message = ' '.join(args)

    if not USER_STATS_FILE.exists():
        await update.message.reply_text(get_text(update.effective_user.id, "broadcast_no_users"))
        return

    users = set()

    try:
        with open(USER_STATS_FILE, "r") as f:
            for line in f:
                user_id = line.strip().split('|')[0].strip()
                if user_id.isdigit():
                    users.add(int(user_id))
    except Exception as e:
        logger.error(f"Ошибка чтения файла пользователей: {e}")
        await update.message.reply_text(get_text(update.effective_user.id, "broadcast_read_error"))
        return

    if not users:
        await update.message.reply_text(get_text(user.id, "broadcast_no_valid"))
        return

    total = len(users)
    success = 0
    failed = 0

    progress_msg = await update.message.reply_text(
        get_text(update.effective_user.id, "broadcast_start").format(total))

    for user_id in users:
        try:
            await context.bot.send_message(chat_id=int(user_id), text=message)
            success += 1
        except Exception as e:
            logger.error(f"Broadcast error for {user_id}: {str(e)}")
            failed += 1

        if (success + failed) % 10 == 0:
            try:
                await progress_msg.edit_text(
                    get_text(update.effective_user.id, "broadcast_progress").format(success + failed, total))
            except:
                pass

    try:
        await progress_msg.delete()
    except:
        pass

    await update.message.reply_text(
        get_text(update.effective_user.id, "broadcast_complete").format(success, failed))

async def off_bot(user, context):
    await admin_wrapper(update, context, _ban_handler)
    log_admin_action(user.id, "BOT_SHUTDOWN")
    await context.application.stop()
    await context.application.shutdown()

    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [t.cancel() for t in tasks]

    os.kill(os.getpid(), signal.SIGTERM)

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    lang = user_lang[user.id]
    
    try:
        # ==================== ПРОВЕРКА ПРАВ ====================
        if not is_admin(user.id):
            log_admin_action(
                admin_id=user.id,
                action="UNAUTHORIZED_ACCESS",
                details={
                    "command": ' '.join(args),
                    "ip": update.message.chat.id,
                    "user_lang": lang
                }
            )
            await update.message.reply_text(get_text(user.id, "access_denied"))
            return

        # ==================== ЛОГИРОВАНИЕ СТАРТА ====================
        log_admin_action(
            admin_id=user.id,
            action="COMMAND_START",
            details={
                "full_command": update.message.text,
                "args": args.copy(),
                "chat_type": update.message.chat.type
            }
        )

        # ==================== ОБРАБОТКА ПОДКОМАНД ====================
        if not args:
            await update.message.reply_text(get_text(user.id, "admin_help"))
            return

        cmd = args[0].lower()
        args = args[1:]  # Удаляем подкоманду из списка аргументов

        try:
            if cmd == "users":
                log_admin_action(user.id, "USER_LIST_REQUEST")
                await users_command(update, context)

            elif cmd == "ban":
                 await handle_ban(update, context)

            elif cmd == "unban":
                await handle_unban(update, context, args)

            elif cmd == "logs":
                log_admin_action(user.id, "LOGS_EXPORT", {"type": "all"})
                await send_zipped_logs(update, context, "logs")

            elif cmd == "stats":
                log_admin_action(user.id, "STATS_REQUEST")
                await stats_command(update, context)

            elif cmd == "broadcast":
                log_admin_action(user.id, "BROADCAST_INIT")
                await broadcast_command(update, context, args)

            elif cmd == "history":
                log_admin_action(user.id, "HISTORY_REQUEST")
                await history_command(update, context)

            # ==================== ЛОГ УСПЕШНОГО ВЫПОЛНЕНИЯ ====================
            log_admin_action(
                admin_id=user.id,
                action="COMMAND_SUCCESS",
                details={
                    "command": cmd,
                    "execution_time": datetime.datetime.now().isoformat(),
                    "args": args
                }
            )
            # ==================== ОБРАБОТКА ОШИБОК КОМАНД ====================
        except Exception as cmd_error:
            logger.error(f"Command '{cmd}' failed: {str(cmd_error)}")
            log_admin_action(
                admin_id=user.id,
                action="COMMAND_FAILED",
                details={
                    "command": cmd,
                    "error": str(cmd_error),
                    "traceback": traceback.format_exc(),
                    "args": args
                }
            )
            await update.message.reply_text(get_text(user.id, "server_error"))

    except Exception as global_error:
        # ==================== ГЛОБАЛЬНАЯ ОБРАБОТКА ОШИБОК ====================
        logger.critical(f"Global admin error: {str(global_error)}")
        log_admin_action(
            admin_id=user.id,
            action="SYSTEM_FAILURE",
            details={
                "error": str(global_error),
                "traceback": traceback.format_exc()
            }
        )
        await update.message.reply_text(get_text(user.id, "critical_error"))
