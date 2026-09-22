import os
import logging
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# === НАСТРОЙКИ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# === ССЫЛКИ ===
CHANNEL_DV = "https://t.me/dvcorpdev"
CHANNEL_VISHNEVY = "https://t.me/CherryJuice"
RULES_URL = "https://telegra.ph/Pravila-servera-DV-Corp-09-22"
MODPACK_URL = "https://t.me/CherryJuice/1649"

# === СОСТОЯНИЯ ===
WAIT_NICK, WAIT_TG, WAIT_AGREE = range(3)
SUPPORT_MSG = 4

logging.basicConfig(level=logging.INFO)

# === ФАЙЛЫ ===
WHITELIST_FILE = "whitelist.json"
BLACKLIST_FILE = "blacklist.json"

def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# === ГЛАВНОЕ МЕНЮ ===
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🚀 Как попасть на сервер?", callback_data="how_to_join")],
        [InlineKeyboardButton("📜 Правила сервера", url=RULES_URL)],
        [InlineKeyboardButton("📢 Телеграм-канал сервера", url=CHANNEL_DV)],
        [InlineKeyboardButton("📢 Телеграм-канал Дмитрия Вишневого", url=CHANNEL_VISHNEVY)],
        [InlineKeyboardButton("📝 Попасть в белый список", callback_data="whitelist")],
        [InlineKeyboardButton("🛠 Поддержка", callback_data="support")],
    ]
    return InlineKeyboardMarkup(keyboard)

MAIN_MENU_TEXT = "Выбери, что тебя интересует:"

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎮 Добро пожаловать на сервер Дмитрия Вишневого «DV_Corp»!\n\n"
        "Выбери, что тебя интересует:"
    )
    await update.message.reply_photo(
        photo=open("images/start.png", "rb"),
        caption=text,
        reply_markup=get_main_menu()
    )

# === /cancel ===
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Действие отменено.",
        reply_markup=get_main_menu()
    )
    return ConversationHandler.END

# === КНОПКИ ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "how_to_join":
        keyboard = [
            [InlineKeyboardButton("💻 ПК (Java)", callback_data="join_pc")],
            [InlineKeyboardButton("📱 Телефон", callback_data="join_phone")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back")],
        ]
        await query.edit_message_media(
            media=InputMediaPhoto(
                media=open("images/vibor.png", "rb"),
                caption="Выбери своё устройство:"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "join_pc":
        text = (
            "💻 **Для ПК (Java Edition):**\n\n"
            "Версия: `1.21.4 Fabric`\n"
            "IP: `DVCorp.minerent.io`\n\n"
            "📦 Сборка модов – по кнопке ниже:"
        )
        keyboard = [
            [InlineKeyboardButton("📦 Скачать сборку", url=MODPACK_URL)],
            [InlineKeyboardButton("⬅️ Назад", callback_data="how_to_join")],
        ]
        await query.edit_message_media(
            media=InputMediaPhoto(
                media=open("images/pc.png", "rb"),
                caption=text,
                parse_mode="Markdown"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "join_phone":
        keyboard = [
            [InlineKeyboardButton("🍎 iOS", callback_data="join_ios")],
            [InlineKeyboardButton("🤖 Android", callback_data="join_android")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="how_to_join")],
        ]
        await query.edit_message_media(
            media=InputMediaPhoto(
                media=open("images/mobile.png", "rb"),
                caption="Выбери свою ОС:"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "join_ios":
        text = (
            "🍎 **Для iOS:**\n\n"
            "Версия: `1.21.4`\n"
            "IP: `DVIOS.minerent.io`\n"
            "Порт: `19138`\n\n"
            "⚠️ Только лицензия."
        )
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="join_phone")]]
        await query.edit_message_media(
            media=InputMediaPhoto(
                media=open("images/mobile.png", "rb"),
                caption=text,
                parse_mode="Markdown"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "join_android":
        text = (
            "🤖 **Для Android:**\n\n"
            "Версия: `1.21.4`\n"
            "IP: `DVCorp.minerent.io`\n"
            "Порт: `19120`"
        )
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="join_phone")]]
        await query.edit_message_media(
            media=InputMediaPhoto(
                media=open("images/mobile.png", "rb"),
                caption=text,
                parse_mode="Markdown"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "back":
        await query.edit_message_media(
            media=InputMediaPhoto(
                media=open("images/start.png", "rb"),
                caption=MAIN_MENU_TEXT
            ),
            reply_markup=get_main_menu()
        )

# === ВАЙТЛИСТ ===
async def whitelist_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("⬅️ Отмена", callback_data="cancel")]]
    await query.edit_message_media(
        media=InputMediaPhoto(
            media=open("images/nickname.png", "rb"),
            caption="Напиши свой ник в Minecraft:"
        ),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return WAIT_NICK

async def get_nick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nick = update.message.text
    blacklist = load_json(BLACKLIST_FILE)

    if any(entry["nick"].lower() == nick.lower() for entry in blacklist):
        await update.message.reply_text("❌ Этот ник в чёрном списке. Заявка отклонена.")
        return ConversationHandler.END

    context.user_data["nick"] = nick
    keyboard = [[InlineKeyboardButton("⬅️ Отмена", callback_data="cancel")]]
    await update.message.reply_photo(
        photo=open("images/nickname.png", "rb"),
        caption="Теперь напиши свой Telegram (@username):",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return WAIT_TG

async def get_tg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tg"] = update.message.text
    keyboard = [
        [InlineKeyboardButton("✅ Я согласен(а) с правилами", callback_data="agree_rules")],
        [InlineKeyboardButton("⬅️ Отмена", callback_data="cancel")],
    ]
    await update.message.reply_photo(
        photo=open("images/nickname.png", "rb"),
        caption="Нажми кнопку ниже, чтобы подтвердить согласие с правилами:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return WAIT_AGREE

async def agree_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    nick = context.user_data.get("nick")
    tg = context.user_data.get("tg")
    user_id = update.effective_user.id
    username = update.effective_user.username

    whitelist = load_json(WHITELIST_FILE)
    repeat = any(entry["user_id"] == user_id for entry in whitelist)

    if repeat:
        await query.edit_message_media(
            media=InputMediaPhoto(
                media=open("images/start.png", "rb"),
                caption="❌ Вы уже подавали заявку.\n\nПо всем вопросам пишите в поддержку."
            ),
            reply_markup=get_main_menu()
        )
        return ConversationHandler.END

    entry = {
        "nick": nick,
        "tg": tg,
        "user_id": user_id,
        "username": username,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    whitelist.append(entry)
    save_json(WHITELIST_FILE, whitelist)

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📝 **Новая заявка:**\n\nНик: `{nick}`\nTG: {tg}\nID: `{user_id}`"
    )

    await query.edit_message_media(
        media=InputMediaPhoto(
            media=open("images/start.png", "rb"),
            caption="✅ Заявка отправлена!\n\n⚠️ Добавление занимает до **2 дней**.\n\nПопробуй зайти, тебя кикнет, потом добавим."
        ),
        reply_markup=get_main_menu()
    )
    return ConversationHandler.END

# === ОТМЕНА ЧЕРЕЗ КНОПКУ ===
async def cancel_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_media(
        media=InputMediaPhoto(
            media=open("images/start.png", "rb"),
            caption="Действие отменено.\n\n" + MAIN_MENU_TEXT
        ),
        reply_markup=get_main_menu()
    )
    return ConversationHandler.END

# === ЧЁРНЫЙ СПИСОК ===
async def blacklist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "Использование:\n"
            "/blacklist add <ник>\n"
            "/blacklist remove <ник>\n"
            "/blacklist list"
        )
        return

    action = args[0].lower()
    blacklist = load_json(BLACKLIST_FILE)

    if action == "add" and len(args) > 1:
        nick = args[1]
        if any(e["nick"].lower() == nick.lower() for e in blacklist):
            await update.message.reply_text(f"Уже в чёрном списке: {nick}")
            return
        blacklist.append({"nick": nick, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        save_json(BLACKLIST_FILE, blacklist)
        await update.message.reply_text(f"✅ Добавлен в чёрный список: {nick}")

    elif action == "remove" and len(args) > 1:
        nick = args[1]
        blacklist = [e for e in blacklist if e["nick"].lower() != nick.lower()]
        save_json(BLACKLIST_FILE, blacklist)
        await update.message.reply_text(f"✅ Удалён из чёрного списка: {nick}")

    elif action == "list":
        if not blacklist:
            await update.message.reply_text("Чёрный список пуст.")
            return
        text = "🚫 **Чёрный список:**\n\n"
        for i, e in enumerate(blacklist, 1):
            text += f"{i}. `{e['nick']}` (добавлен {e['date']})\n"
        await update.message.reply_text(text, parse_mode="Markdown")

    else:
        await update.message.reply_text("Неверная команда. Используй /blacklist add|remove|list")

# === ПРОВЕРКА НИКА ===
async def check_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("Использование: /check <ник>")
        return

    nick = context.args[0]
    whitelist = load_json(WHITELIST_FILE)
    blacklist = load_json(BLACKLIST_FILE)

    in_white = any(e["nick"].lower() == nick.lower() for e in whitelist)
    in_black = any(e["nick"].lower() == nick.lower() for e in blacklist)

    if in_black:
        await update.message.reply_text(f"🚫 `{nick}` – в ЧЁРНОМ списке", parse_mode="Markdown")
    elif in_white:
        entry = next(e for e in whitelist if e["nick"].lower() == nick.lower())
        await update.message.reply_text(
            f"✅ `{nick}` – в БЕЛОМ списке\nTG: {entry['tg']}\nДата: {entry['date']}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(f"❓ `{nick}` – не найден", parse_mode="Markdown")

# === ПОДДЕРЖКА ===
async def support_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("⬅️ Отмена", callback_data="cancel")]]
    await query.edit_message_media(
        media=InputMediaPhoto(
            media=open("images/podderzhka.png", "rb"),
            caption="Напиши своё сообщение для поддержки:"
        ),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return SUPPORT_MSG

async def support_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    user = update.message.from_user

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🛠 **Поддержка:**\n\nОт: @{user.username}\n\n{msg}"
    )
    await update.message.reply_text("✅ Отправлено!")

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open("images/start.png", "rb"),
        caption=MAIN_MENU_TEXT,
        reply_markup=get_main_menu()
    )
    return ConversationHandler.END

# === СПИСОК ЗАЯВОК ===
async def list_whitelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    data = load_json(WHITELIST_FILE)
    if not data:
        await update.message.reply_text("Заявок нет.")
        return

    text = "📋 **Все заявки:**\n\n"
    for i, entry in enumerate(data, 1):
        text += f"{i}. Ник: `{entry['nick']}`\n   TG: {entry['tg']}\n   Дата: {entry['date']}\n\n"

    await update.message.reply_text(text, parse_mode="Markdown")

# === ЗАПУСК ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("list", list_whitelist))
    app.add_handler(CommandHandler("blacklist", blacklist_cmd))
    app.add_handler(CommandHandler("check", check_cmd))
    app.add_handler(CallbackQueryHandler(cancel_button, pattern="^cancel$"))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(how_to_join|join_pc|join_phone|join_ios|join_android|back)$"))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(whitelist_start, pattern="^whitelist$")],
        states={
            WAIT_NICK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_nick)],
            WAIT_TG: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_tg)],
            WAIT_AGREE: [CallbackQueryHandler(agree_rules, pattern="^agree_rules$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(support_start, pattern="^support$")],
        states={
            SUPPORT_MSG: [MessageHandler(filters.TEXT & ~filters.COMMAND, support_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    ))

    app.run_polling()

if __name__ == "__main__":
    main()
